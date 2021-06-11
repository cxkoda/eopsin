import enum
from datetime import timedelta

import sqlalchemy as sql

from ._sqlbase import Base
from .timestamp import TimeStamp


@enum.unique
class Interval(enum.Enum):
    MINUTE_1 = '1m'
    MINUTE_5 = '5m'
    MINUTE_15 = '15m'
    HOUR_1 = '1h'
    HOUR_4 = '4h'
    DAY_1 = '1d'
    WEEK_1 = '1w'

    def timedelta(self):
        if self == self.MINUTE_1:
            return timedelta(minutes=1)
        elif self == self.MINUTE_5:
            return timedelta(minutes=5)
        elif self == self.MINUTE_15:
            return timedelta(minutes=15)
        elif self == self.HOUR_1:
            return timedelta(hours=1)
        elif self == self.HOUR_4:
            return timedelta(hours=4)
        elif self == self.DAY_1:
            return timedelta(days=1)
        elif self == self.WEEK_1:
            return timedelta(weeks=1)


class Candle(Base):
    __tablename__ = 'candle'
    __table_args__ = (sql.UniqueConstraint('exchange_id', 'pair_id', 'interval', 'openTime', name='_candle_unique'),
                      )
    id = sql.Column(sql.Integer, primary_key=True)
    exchange_id = sql.Column(sql.Integer, sql.ForeignKey('exchange.id'))
    exchange = sql.orm.relationship("Exchange")
    pair_id = sql.Column(sql.Integer, sql.ForeignKey('pair.id'))
    pair = sql.orm.relationship("Pair")
    interval = sql.Column(sql.Enum(Interval))

    openTime = sql.Column(TimeStamp)
    closeTime = sql.Column(TimeStamp)

    open = sql.Column(sql.Float)
    high = sql.Column(sql.Float)
    low = sql.Column(sql.Float)
    close = sql.Column(sql.Float)
    volume = sql.Column(sql.Float)
    quoteAssetVolume = sql.Column(sql.Float)
    numberOfTrades = sql.Column(sql.Integer)
    takerBuyBaseAssetVolume = sql.Column(sql.Float)
    takerBuyQuoteAssetVolume = sql.Column(sql.Float)

    def __repr__(self):
        return f'{self.pair} {self.interval} {self.openTime}: {self.open} -> {self.close}'
