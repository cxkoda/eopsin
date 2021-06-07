import datetime as dt


def floorDatetime(date: dt.datetime, resolution: dt.timedelta, tz=None) -> dt.datetime:
    if tz is None:
        if date.tzinfo is None:
            tz = date.astimezone().tzinfo
        else:
            tz = date.tzinfo

    reference = dt.datetime(2000, 1, 1, tzinfo=tz)
    diff = date.astimezone(tz) - reference
    delta = diff % resolution
    return date - delta


def ceilDatetime(date: dt.datetime, resolution: dt.timedelta, tz=dt.timezone.utc) -> dt.datetime:
    floored = floorDatetime(date, resolution, tz)
    if floored == date:
        return date
    else:
        return floored + resolution
