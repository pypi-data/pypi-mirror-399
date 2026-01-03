from datetime import datetime, date, time, timedelta
import re
import yarl
from functools import wraps
from typing import Optional, Union
from ..types import QualityRating
import dateutil.parser as dtparser

INVALID_STRING_INPUTS = ['', '?', 'unknown', 'no score']


def catch_dirty_strings(func):
  @wraps(func)
  def wrapper(v: Union[str, None], *args, **kwargs):
    if any(
      [
        v is None,
        (isinstance(v, str) and v.lower() in INVALID_STRING_INPUTS),
      ]
    ):
      return None

    return func(v, *args, **kwargs)

  return wrapper


@catch_dirty_strings
def validate_url(s: str) -> yarl.URL:
  if not s.startswith('https:'):
    s = f'https:{s}'
  return yarl.URL(s)


FLOAT_PATTERN = re.compile(r'([-+]?\d*\.?\d+)')


@catch_dirty_strings
def validate_float(s: str) -> Optional[float]:
  match = FLOAT_PATTERN.match(s)
  if match:
    try:
      return float(match.group(1))
    except ValueError:
      return None
  return None


@catch_dirty_strings
def validate_date(s: str) -> Optional[date]:
  try:
    return datetime.fromisoformat(s)

  except:
    return None


@catch_dirty_strings
def validate_string(s: str) -> str:
  return s


@catch_dirty_strings
def validate_time(s: str) -> Optional[time]:
  try:
    # dateutil.parser.parse handles ISO, AM/PM, and messy spacing
    # all in one go. We just call .time() on the result.
    return dtparser.parse(s).time()

  except (ValueError, OverflowError, TypeError):
    # Fallback: if the string is just numbers or totally broken
    return None


@catch_dirty_strings
def validate_timedelta(s: str) -> Optional[timedelta]:
  try:
    # dateutil handles "12:25:39", "4:08", and even "1h 30m"
    dt = dtparser.parse(s)
    # Calculate duration since the start of that day
    return timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)

  except (ValueError, OverflowError):
    # Fallback for the really weird cases
    return None


@catch_dirty_strings
def validate_boolean(s: str) -> bool:
  if s.lower().startswith('yes'):
    return True
  elif s.lower().startswith('no'):
    return False
  else:
    raise ValueError(s)


@catch_dirty_strings
def validate_xc_file_upload_url(s: str) -> yarl.URL:
  if s.startswith('//'):
    s = f'https:{s}'

  invalid_values = ['', '?', 'unknown']
  if s.lower() in invalid_values:
    raise ValueError(f"Field received an invalid placeholder value: '{s}'")

  PATTERN = (
    r'^https?://xeno-canto\.org/sounds/uploaded'
    r'/(?P<user_id>[^/]+)'
    r'/(?:ffts|wave)'  # "ffts"=sonogram, "wave"=oscillogram
    r'/XC(?P<recording_id>\d+)'
    r'-(?P<version>small|med|large|full)'
    r'\.(?P<file_ext>[a-z0-9]+)$'
  )

  match = re.match(PATTERN, s)

  if not match:
    raise ValueError(s)

  # metadata = match.groupdict() # TODO Something with this

  return yarl.URL(s)


@catch_dirty_strings
def validate_xc_recording_quality(v: str) -> Optional[QualityRating]:
  try:
    return QualityRating[v.capitalize()]

  except:
    return None
