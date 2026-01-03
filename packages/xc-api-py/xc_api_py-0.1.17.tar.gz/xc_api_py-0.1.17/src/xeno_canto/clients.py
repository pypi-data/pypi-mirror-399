from .schemas.search_query import SearchQuery, SearchQuerySchema
from .schemas.recording import XenoCantoRecordingSchema, XenoCantoRecordingLean
from .schemas.api_response import ApiResponseSchema
from .session import CachedSessionManager, SessionManager
from .errors import ClientError, ServerError
from .types import RecordingId

from concurrent.futures import (
  ThreadPoolExecutor,
  as_completed,
)
from typing import (
  Optional,
  Iterator,
  Union,
  Sequence,
  Dict,
  List,
  Any,
  Unpack,
  Tuple,
  Set,
  overload,
)
import warnings
import re
from os import cpu_count
from datetime import timedelta
from pydantic import ValidationError
import random


class Client:
  _BASE_URL = 'https://xeno-canto.org/api/3'
  _PER_PAGE_MIN = 50
  _PER_PAGE_MAX = 500
  _XC_ID_PATTERN = re.compile(r'(?i:xc)?(?P<id>\d+)')
  _XC_MAX_ID = 950000
  _MAX_WORKERS = min(6, cpu_count() or 1)

  # @overload
  def __init__(
    self,
    api_key: str,
    use_cache: bool = False,
    cache_name: str = 'client',
    cache_age: Optional[Union[int, timedelta]] = None,
    verbose: bool = False,
  ):
    self._api_key = api_key
    self._verbose = verbose

    if use_cache:
      self._manager = CachedSessionManager()
    else:
      self._manager = SessionManager()

  @property
  def _session(self):
    return self._manager.session

  def _fetch_from_api(
    self,
    search_query: Union[SearchQuerySchema, Dict[str, Any]],
    page: int,
    retries: int = 0,
  ) -> ApiResponseSchema:
    # TODO Implement retries

    if page < 1:
      raise ValueError(page)

    if isinstance(search_query, SearchQuerySchema):
      query_dict = search_query.model_dump(
        by_alias=True,
        exclude_none=True,
      )

    else:
      query_dict = search_query

    query_string = '+'.join(f'{k}:{v}' for k, v in query_dict.items())

    params = dict(
      key=self._api_key,
      per_page=self._PER_PAGE_MAX,
      page=page,
      query=query_string,
    )

    params_string = '&'.join(f'{k}={v}' for k, v in params.items())

    url = f'{self._BASE_URL}/recordings?{params_string}'
    resp = self._session.get(url)

    match resp.status_code:
      case 401:
        body = resp.json()
        msg = body.get(
          'message',
          "Missing or invalid 'key' parameter. Visit https://xeno-canto.org/account to retrieve your API key.",
        )
        raise ClientError(msg) from None

      case 400:
        body = resp.json()
        msg = body.get(
          'message',
          'Xeno-canto API v3 only accepts queries using tags. Visit https://xeno-canto.org/explore/api for a complete list.',
        )
        raise ClientError(f'{msg} ({resp.url})') from None

      case 503:
        raise ServerError(
          'Server responded with 503, you probably hit the rate-limit: https://xeno-canto.org/explore/api'
        ) from None

    resp.raise_for_status()
    return ApiResponseSchema.model_validate_json(resp.text)

  def _probe_api(self, query: SearchQuerySchema) -> ApiResponseSchema:
    return self._fetch_from_api(query, page=1)

  def _search(self, query: Union[SearchQuery, Dict[str, Any]]) -> Iterator[XenoCantoRecordingSchema]:
    limit = None
    if 'limit' in query:
      limit = query.pop('limit')
    try:
      search_query = SearchQuerySchema.model_validate(query)

    except ValidationError as e:
      raise ValueError(f'Invalid search query: {e}')

    if limit is not None and not (1 <= limit <= 100000):
      raise ValueError(limit)

    probe = self._probe_api(search_query)
    if not probe.recordings:
      return

    yielded_count = 0

    for recording in probe.recordings:
      yield recording
      yielded_count += 1
      if limit and yielded_count >= limit:
        return

    total_pages = probe.num_pages
    if total_pages <= 1:
      return

    remaining_pages = range(2, total_pages + 1)

    with ThreadPoolExecutor(max_workers=self._MAX_WORKERS) as executor:
      # Map page numbers to futures
      future_to_page = {executor.submit(self._fetch_from_api, search_query, page): page for page in remaining_pages}

      for future in as_completed(future_to_page):
        resp = future.result()
        if not resp or not resp.recordings:
          continue

        for recording in resp.recordings:
          yield recording
          yielded_count += 1

          if limit and yielded_count >= limit:
            # Cancel pending futures if possible and return
            executor.shutdown(wait=False, cancel_futures=True)
            return

  def _sanitize_ids(self, recording_ids: Sequence[Union[str, int]]) -> Tuple[Set[int], Set[Any]]:
    cleaned = set()
    malformed = set()

    for rid in recording_ids:
      if match := self._XC_ID_PATTERN.fullmatch(str(rid).strip()):
        cleaned.add(int(match.group('id')))
      else:
        malformed.add(rid)

    return cleaned, malformed

  def _warn_failed_ids(self, failed: List[int]) -> None:
    failed = sorted(list(failed))
    if len(failed) >= 10:
      failed_str = (
        '[' + ', '.join([*[str(i) for i in failed[:10]], '...', str(failed[-1])]) + f'] (total: {len(failed)})'
      )
    warnings.warn(f'Failed to fetch the following ids: {failed_str}')

  def _warn_malformed_ids(self, malformed: List[int]) -> None:
    malformed_str = [f'{m}' for m in malformed]
    warnings.warn(
      f'Skipping invalid XC recording catalogue numbers - see https://xeno-canto.org/explore/api for more info; {malformed_str}'
    )

  def _search_ids_range(self, start: int, end: int) -> Iterator[XenoCantoRecordingSchema]:
    if not (start > 1 and end > 1):
      raise ValueError((start, end))

    low, high = (start, end) if start < end else (end, start)

    ex = ThreadPoolExecutor(max_workers=self._MAX_WORKERS)

    # TODO Divide range into batches
    batch_size = self._PER_PAGE_MAX
    batches: List[Tuple[int, int]] = []
    for i in range(low, high + 1, batch_size):
      j = min(i + batch_size - 1, high)
      batches.append((i, j))

    def _fetch_batch(start: int, end: int):
      return list(self._search({'nr': f'{start}-{end}'})), (start, end)

    future_to_batch = {
      ex.submit(
        _fetch_batch,
        i,
        j,
      ): (i, j)
      for i, j in batches
    }

    failed = set()

    try:
      for future in as_completed(future_to_batch):
        try:
          recordings, (i, j) = future.result()
          yield from recordings
        except:
          failed.update(range(i, j + 1))

    finally:
      if self._verbose and failed:
        self._warn_failed_ids(list(failed))

      ex.shutdown(wait=False, cancel_futures=True)

  def _search_ids_scattered(self, recording_ids: Sequence[Union[str, int]]) -> Iterator[XenoCantoRecordingSchema]:
    cleaned, malformed = self._sanitize_ids(recording_ids)

    if malformed and self._verbose:
      self._warn_malformed_ids(list(malformed))

    def _fetch_one_by_id(xc_id: int):
      resp = self._fetch_from_api(
        search_query={'nr': xc_id},
        page=1,
      )
      return resp.recordings[0] if resp else None

    ex = ThreadPoolExecutor(max_workers=self._MAX_WORKERS)
    future_to_id = {ex.submit(_fetch_one_by_id, rid): rid for rid in cleaned}

    failed = set()

    try:
      for future in as_completed(future_to_id):
        rid = future_to_id[future]
        res = future.result()
        if res:
          yield res
        else:
          failed.add(rid)

    finally:
      if self._verbose and failed:
        self._warn_failed_ids(list(failed))

      ex.shutdown(wait=False, cancel_futures=True)

  def _search_ids(
    self, ids_or_range: Union[List[RecordingId], Tuple[RecordingId, RecordingId]], /
  ) -> Iterator[XenoCantoRecordingSchema]:
    if isinstance(ids_or_range, List):
      return self._search_ids_scattered(ids_or_range)

    elif isinstance(ids_or_range, Tuple):
      start, end = ids_or_range
      return self._search_ids_range(int(start), int(end))

    raise ValueError(ids_or_range)

  def _sample(self, k: int):
    if not 1 <= k <= 1000:
      raise ValueError(k)

    res: List[XenoCantoRecordingSchema] = []
    seen = set()

    while len(res) < k:
      needed = k - len(res)
      batch_ids = []
      while len(batch_ids) < (needed * 2):
        rid = random.randint(1, self._XC_MAX_ID)
        if rid not in seen:
          batch_ids.append(rid)
          seen.add(rid)

      for recording in self._search_ids_scattered(batch_ids):  # _search_ids_scattered or _search_ids_range?
        res.append(recording)
        if len(res) >= k:
          break

    return sorted(random.sample(res, k), key=lambda r: r.recording_number)

  def _get_one(self, recording_id: Union[str, int]):
    recordings = self._search(SearchQuery(recording_number=recording_id))
    try:
      return next(recordings)

    except StopIteration:
      return None

  ###################### Public API

  @overload
  def search(self, **kwargs: Unpack[SearchQuery]) -> Iterator[XenoCantoRecordingSchema]: ...

  @overload
  def search(self, query: SearchQuery) -> Iterator[XenoCantoRecordingSchema]: ...

  def search(self, query: Optional[SearchQuery] = None, **kwargs: Unpack[SearchQuery]):
    if query:
      return self._search(query)
    else:
      return self._search(kwargs)

  @overload
  def search_ids(self, recording_ids: List[RecordingId], /): ...

  @overload
  def search_ids(self, range: Tuple[RecordingId, RecordingId], /): ...

  def search_ids(
    self, ids_or_range: Union[List[RecordingId], Tuple[RecordingId, RecordingId]]
  ) -> Iterator[XenoCantoRecordingSchema]:
    return self._search_ids(ids_or_range)

  def sample(self, k: int):
    return self._sample(k)

  def __getitem__(
    self, key: Union[str, int, slice]
  ) -> Union[XenoCantoRecordingSchema, Iterator[XenoCantoRecordingSchema]]:
    if isinstance(key, slice):
      if key.start is None or key.stop is None:
        raise ValueError()
      return self.search_ids((key.start, key.stop))

    r = self._get_one(key)
    if r is None:
      raise IndexError(key)
    return r


class LeanClient(Client):
  def __init__(
    self,
    api_key: str,
  ):
    self._api_key = api_key
    self._verbose = False
    self._manager = SessionManager()

  ###################### Public API

  @overload
  def search(self, **kwargs: Unpack[SearchQuery]) -> Iterator[XenoCantoRecordingLean]: ...

  @overload
  def search(self, query: SearchQuery) -> Iterator[XenoCantoRecordingLean]: ...

  def search(
    self, query: Optional[SearchQuery] = None, **kwargs: Unpack[SearchQuery]
  ) -> Iterator[XenoCantoRecordingLean]:
    rs = super().search(query if query is not None else kwargs)
    return (r.lean for r in rs)

  @overload
  def search_ids(self, recording_ids: List[RecordingId], /): ...

  @overload
  def search_ids(self, range: Tuple[RecordingId, RecordingId], /): ...

  def search_ids(self, ids_or_range: Union[List[RecordingId], Tuple[RecordingId, RecordingId]]):
    rs = super().search_ids(ids_or_range)
    return (r.lean for r in rs)

  def sample(self, k: int):
    rs = super().sample(k)
    return [r.lean for r in rs]

  def __getitem__(self, key: Union[str, int, slice]) -> Union[XenoCantoRecordingLean, Iterator[XenoCantoRecordingLean]]:
    rs = super().__getitem__(key)
    if isinstance(key, slice):
      return (r.lean for r in rs)  # type: ignore

    return rs.lean  # type: ignore
