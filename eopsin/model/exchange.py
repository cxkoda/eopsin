import sqlalchemy as sql

from ._sqlbase import Base


class Exchange(Base):
    __tablename__ = 'exchange'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)

    def __repr__(self):
        return f'Exchange<id={self.id}, name={self.name}>'
