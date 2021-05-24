from sqlalchemy import Column, Integer, String
from model._sqlbase import Base


class Exchange(Base):
    __tablename__ = 'exchange'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return self.name
