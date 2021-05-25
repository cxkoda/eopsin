from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import timedelta

from model._sqlbase import Base


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
    __table_args__ = (UniqueConstraint('pair_id', 'interval', 'openTime', name='_candle_unique'),
                      )
    id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, ForeignKey('pair.id'))
    pair = relationship("Pair")
    interval = Column(Enum(Interval))

    openTime = Column(DateTime)
    closeTime = Column(DateTime)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    quoteAssetVolume = Column(Float)
    numberOfTrades = Column(Integer)
    takerBuyBaseAssetVolume = Column(Float)
    takerBuyQuoteAssetVolume = Column(Float)

    def __repr__(self):
        return f'{self.pair} {self.interval} {self.openTime}: {self.open} -> {self.close}'
