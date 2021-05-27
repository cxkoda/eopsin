from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from model._sqlbase import Base


class Pair(Base):
    __tablename__ = 'pair'
    __table_args__ = (UniqueConstraint('asset', 'currency', name='_pair_unique'),
                      )
    id = Column(Integer, primary_key=True)
    asset = Column(String)
    currency = Column(String)

    def __repr__(self):
        return f'{self.asset}_{self.currency}'
