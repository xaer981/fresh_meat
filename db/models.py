from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (column_property, mapped_column, relationship,
                            validates)

from .database import Base, SessionLocal
from .exceptions import ValidationError

session = SessionLocal()


class RawType(Base):
    name = Column(String(length=200), unique=True, nullable=False)
    count_per_one = relationship('CountPerOne', back_populates='type')
    amount = relationship('RawAmount', back_populates='type')

    @validates('name', include_backrefs=False)
    def validate_name(self, key, name):
        if not name:

            raise ValidationError('Введите название')

        if session.query(RawType).filter_by(name=name).first():

            raise ValidationError('Такой вид мяса уже существует')

        if len(name) > 200:

            raise ValidationError('Слишком длинное название вида')

        return name


class CountPerOne(Base):
    type = relationship('RawType', back_populates='count_per_one')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    _amount = mapped_column('amount', Float, unique=False, nullable=False)

    @hybrid_property
    def amount(self):

        return self._amount * 1000

    @amount.setter
    def amount(self, amount):
        self._amount = amount / 1000

    @validates('_amount')
    def validate_amount(self, key, amount):
        if not amount:

            raise ValidationError('Введите количество на порцию')

        if amount <= 0:

            raise ValidationError('Количество на порцию '
                                  'не может быть меньше/равно нулю')

        try:
            float(amount)

        except ValueError:

            raise ValidationError('Это не число')

        return amount


class RawAmount(Base):
    type = relationship('RawType', back_populates='amount')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    fridge = Column(Float, unique=False, nullable=False, default=0)
    freezer = Column(Float, unique=False, nullable=False)
    total = column_property(fridge + freezer)

    @validates('freezer')
    def validate_amount(self, key, freezer):
        try:
            float(freezer)

        except ValueError:

            raise ValidationError('Это не число')

        return freezer
