from ..types import QualityRating

import yarl
import datetime
from typing import Any
import re


def serialize_yarl(v: Any) -> Any:
  if isinstance(v, yarl.URL):
    return str(v)
  return v


def serialize_quality_rating(v: Any) -> Any:
  if isinstance(v, QualityRating):
    return v.name
  return v


def serialize_datetime_date(v: Any) -> Any:
  if isinstance(v, datetime.date):
    return v.isoformat()
  return v


LICENSE_PATTERN = re.compile(r'/licenses/(?P<license>[a-z-]+)/(?P<version>\d+\.\d+)/')


def serialize_license(v: Any) -> Any:
  if isinstance(v, yarl.URL):
    if match := LICENSE_PATTERN.search(str(v)):
      d = match.groupdict()
      lic = d.get('license')
      ver = d.get('version')
      return f'{lic},{ver}'
