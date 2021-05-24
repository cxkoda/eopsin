from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from model._sqlbase import Base


class Pair(Base):
    __tablename__ = 'pair'
    __table_args__ = (UniqueConstraint('exchange_id', 'asset', 'currency', name='_pair_unique'),
                      )
    id = Column(Integer, primary_key=True)
    exchange_id = Column(Integer, ForeignKey('exchange.id'))
    exchange = relationship("Exchange")
    asset = Column(String)
    currency = Column(String)

    def __repr__(self):
        return f'{self.exchange}-{self.asset}_{self.currency}'
