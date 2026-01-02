import typing
import zoneinfo
from datetime import datetime, timezone
from tzlocal import get_localzone

from everai import constants


def format_datetime(t: datetime,
                    fmt: str = '%Y-%m-%dT%H:%M:%S%z',
                    tz: typing.Optional[str | zoneinfo.ZoneInfo] = None) -> str:

    tz = tz or get_localzone() if constants.EVERAI_USE_LOCAL_TIMEZONE else timezone.utc
    ret = t.astimezone(tz).strftime(fmt)
    if ret == '1970-01-01T00:00:00+0000':
        ret = ''
    return ret


def parse_datetime(s: str,
                   fmt: str = '%Y-%m-%dT%H:%M:%S%z',
                   tz: typing.Optional[str | zoneinfo.ZoneInfo] = None) -> datetime:

    tz = tz or get_localzone() if constants.EVERAI_USE_LOCAL_TIMEZONE else timezone.utc
    return datetime.astimezone(tz).strptime(s, fmt)
