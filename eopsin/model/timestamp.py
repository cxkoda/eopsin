import sqlalchemy as sql
import datetime as dt


class TimeStamp(sql.types.TypeDecorator):
    impl = sql.types.DateTime
    LOCAL_TIMEZONE = dt.datetime.utcnow().astimezone().tzinfo
    cache_ok = True

    def process_bind_param(self, value: dt.datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(dt.timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=dt.timezone.utc)

        return value.astimezone(dt.timezone.utc)
