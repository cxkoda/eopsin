import datetime as dt


def floorDatetime(date: dt.datetime, resolution: dt.timedelta,
                  reference=dt.datetime(2000, 1, 1, 0, 0, 0)) -> dt.datetime:
    # There was a problem using datetime.timestamp(). Apparently there is a jump in hours around new-year 2000.
    # Using a manual reference point for now
    diff = date - reference
    delta = diff % resolution
    return date - delta


def ceilDatetime(date: dt.datetime, resolution: dt.timedelta) -> dt.datetime:
    floored = floorDatetime(date, resolution)
    if floored == date:
        return date
    else:
        return floored + resolution
