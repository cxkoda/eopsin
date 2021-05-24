from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from model._sqlbase import Base


class Candle(Base):
    __tablename__ = 'candle'
    __table_args__ = (UniqueConstraint('pair_id', 'interval', 'openTime', name='_candle_unique'),
                      )

    id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, ForeignKey('pair.id'))
    pair = relationship("Pair")
    interval = Column(String)

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
