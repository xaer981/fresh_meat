from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import column_property, relationship

from .database import Base


class RawType(Base):
    name = Column(String(length=200), unique=True, nullable=False)
    count_per_one = relationship('CountPerOne', back_populates='type')
    amount = relationship('RawAmount', back_populates='type')


class CountPerOne(Base):
    type = relationship('RawType', back_populates='count_per_one')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    amount = Column(Integer, unique=False, nullable=False)


class RawAmount(Base):
    type = relationship('RawType', back_populates='amount')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    fridge = Column(Float, unique=False, nullable=False)
    freezer = Column(Float, unique=False, nullable=False)
    total = column_property(fridge + freezer)
