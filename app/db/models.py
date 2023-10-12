from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import column_property, relationship, validates

from .database import Base, SessionLocal
from .exceptions import ValidationError

session = SessionLocal()


class RawType(Base):
    name = Column(String(length=200), unique=True, nullable=False)
    dishes = relationship('Dish', back_populates='type')
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


class Dish(Base):
    type = relationship('RawType', back_populates='dishes')
    type_id = Column(Integer, ForeignKey('rawtype.id'))
    amount = Column(Integer, unique=False, nullable=False)
    name = Column(String(length=200), unique=True, nullable=False)

    @validates('amount')
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
    fridge = Column(Integer, unique=False, nullable=False, default=0)
    freezer = Column(Integer, unique=False, nullable=False, default=0)
    total = column_property(fridge + freezer)

    @validates('freezer')
    def validate_amount(self, key, freezer):
        try:
            float(freezer)

        except ValueError:

            raise ValidationError('Это не число')

        return freezer
