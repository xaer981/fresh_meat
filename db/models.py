from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import column_property, relationship

from .database import Base


class RawType(Base):
    name = Column(String(length=200), unique=True, nullable=False)
    count_per_one = relationship('CountPerOne', back_populates='type_name')
    amount = relationship('RawAmount', back_populates='type_name')


class CountPerOne(Base):
    type_name = relationship('RawType', back_populates='count_per_one')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    amount = Column(Integer, unique=False, nullable=False)


class RawAmount(Base):
    type_name = relationship('RawType', back_populates='amount')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    fridge = Column(Integer, unique=False, nullable=False)
    freezer = Column(Integer, unique=False, nullable=False)
    total = column_property(fridge + freezer)
