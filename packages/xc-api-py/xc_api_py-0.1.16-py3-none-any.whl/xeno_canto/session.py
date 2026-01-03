from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin
from pyrate_limiter import SQLiteBucket
from pathlib import Path
from typing import Optional, Union
from datetime import timedelta
from os import PathLike


class CachedLimiterSession(CacheMixin, LimiterMixin, Session): ...


class LimiterSession(LimiterMixin, Session): ...


class SessionManager:
  session: LimiterSession

  def __init__(self):
    self.session = LimiterSession(
      allowable_methods=['GET'],
      # Rate-limiting
      per_second=4,
    )


class CachedSessionManager:
  session: CachedLimiterSession

  def __init__(
    self,
    cache_dir: Union[str, Path, PathLike[str]] = './.xc_api_cache/client',
    cache_name: str = 'session-cache',
    cache_age: Optional[Union[int, timedelta]] = None,
  ):
    if len(cache_name) < 1:
      raise ValueError(cache_name)

    if not isinstance(cache_dir, Path):
      cache_dir = Path(cache_dir)

    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / f'{cache_name}.db'

    if isinstance(cache_age, int):
      if cache_age < 1:
        raise ValueError(cache_age)
      expire_after = cache_age
    elif isinstance(cache_age, timedelta):
      sec = cache_age.total_seconds()
      if sec < 1:
        raise ValueError(cache_age)
      expire_after = sec
    else:
      expire_after = -1

    self.session = CachedLimiterSession(
      allowable_methods=['GET'],
      # Caching
      cache_name=cache_path,
      expire_after=expire_after,
      backend='sqlite',
      # Rate-limiting
      per_second=4,
      bucket_class=SQLiteBucket,
      bucket_kwargs=dict(
        path=f'{cache_dir.as_posix()}/{cache_name}-rate-limit.db',
        isolation_level='EXCLUSIVE',
        check_same_thread=False,
        timeout=30,
      ),
    )

  def restart_connection(self):
    """Safely closes and re-opens the SQLite cache connection."""
    try:
      # Close the underlying sqlite3 connection
      self.session.cache.responses.close()

      # Re-trigger WAL mode on the new connection
      with self.session.cache.responses.connection() as conn:
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')

      print('Cache connection restarted successfully.')
    except Exception as e:
      print(f'Failed to restart cache connection: {e}')


__all__ = ['CachedSessionManager']
