from datetime import datetime, timedelta


def floorDatetime(date: datetime, resolution: timedelta, reference=datetime(2000, 1, 1, 0, 0, 0)):
    # There was a problem using datetime.timestamp(). Apparently there is a jump in hours around new-year 2000.
    # Using a manual reference point for now
    diff = date - reference
    delta = diff % resolution
    return date - delta


def ceilDatetime(date: datetime, resolution: timedelta):
    floored = floorDatetime(date, resolution)
    if floored == date:
        return date
    else:
        return floored + resolution
