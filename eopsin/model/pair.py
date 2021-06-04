import sqlalchemy as sql

from ._sqlbase import Base


class Pair(Base):
    __tablename__ = 'pair'
    __table_args__ = (sql.UniqueConstraint('asset', 'currency', name='_pair_unique'),
                      )
    id = sql.Column(sql.Integer, primary_key=True)
    asset = sql.Column(sql.String)
    currency = sql.Column(sql.String)

    def __repr__(self):
        return f'{self.asset}_{self.currency}'
