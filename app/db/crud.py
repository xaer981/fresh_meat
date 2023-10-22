from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from .exceptions import ValidationError
from .models import Dish, RawAmount, RawType


class CRUD:
    @staticmethod
    def get_total(session: Session):

        return (session.query(RawType.name, RawAmount.total)
                .select_from(RawAmount)
                .join(RawAmount.type)
                .order_by(RawType.name)
                .all())

    @staticmethod
    def get_fridge(session: Session):

        return (session.query(RawType.name, RawAmount.fridge)
                .select_from(RawAmount)
                .join(RawAmount.type)
                .order_by(RawType.name)
                .all())

    @staticmethod
    def get_freezer(session: Session):

        return (session.query(RawType.name, RawAmount.freezer)
                .select_from(RawAmount)
                .join(RawAmount.type)
                .order_by(RawType.name)
                .all())

    @staticmethod
    def get_types(session: Session):

        return session.query(RawType.name).order_by(RawType.name).all()

    @staticmethod
    def get_dishes(session: Session):

        return (session.query(Dish.name, RawType.name, Dish.amount)
                .select_from(RawType)
                .join(RawType.dishes)
                .order_by(Dish.name)
                .all())

    @staticmethod
    def get_types_names(session: Session):

        return session.execute(select(RawType.name)
                               .order_by(RawType.name)).scalars().all()

    @staticmethod
    def get_dishes_names(session: Session, used_names: list = None):
        if used_names is not None:
            return session.execute(select(Dish.name)
                                   .where(Dish.name.not_in(used_names))
                                   .order_by(Dish.name)).scalars().all()

        return session.execute(select(Dish.name)
                               .order_by(Dish.name)).scalars().all()

    @staticmethod
    def get_type_freezer(session: Session, name: str):
        type = session.query(RawType).filter_by(name=name).first()

        return session.execute(select(RawAmount.freezer)
                               .where(RawAmount.type == type)).scalar()

    @staticmethod
    def get_type_fridge(session: Session, name: str):
        type = session.query(RawType).filter_by(name=name).first()

        return session.execute(select(RawAmount.fridge)
                               .where(RawAmount.type == type)).scalar()

    @staticmethod
    def add_type(session: Session, name: str):
        if not name:

            raise ValidationError('Поле названия обязательно для заполнения!')

        new_type = RawType(name=name)

        session.add(new_type)
        session.commit()

    @staticmethod
    def delete_type(session: Session, name: str):
        if not name:

            raise ValidationError('Нельзя удалить то, чего нет')

        db_type = session.query(RawType).filter_by(name=name).first()

        session.delete(db_type)
        session.commit()

    @staticmethod
    def add_dish(session: Session, data: dict[str, int]):
        type_name = data.get('name')
        count_per_one = data.get('count_per_one')
        dish_name = data.get('dish_name')

        if not type_name:

            raise ValidationError('Поле названия сырья '
                                  'обязательно для заполнения!')

        if not count_per_one:

            raise ValidationError('Поле количества на порцию '
                                  'обязательно для заполнения!')

        if not dish_name:

            raise ValidationError('Поле названия блюда '
                                  'обязательно для заполнения!')

        try:
            float(count_per_one)

        except ValueError:

            raise ValidationError('Это не число')

        db_type = session.query(RawType).filter_by(name=type_name).first()

        new_dish = Dish(type=db_type,
                        amount=int(count_per_one),
                        name=dish_name)
        session.add(new_dish)

        session.commit()

    @staticmethod
    def update_dish(session: Session, data: dict[str, int]):
        name = data.get('name')
        count_per_one = data.get('count_per_one')

        if not name:

            raise ValidationError('Поле названия обязательно для заполнения')

        if not count_per_one:

            raise ValidationError('Поле количества на порцию '
                                  'обязательно для заполнения!')

        try:
            float(count_per_one)

        except ValueError:

            raise ValidationError('Это не число')

        dish = session.query(Dish).filter_by(name=name).first()

        dish.amount = int(count_per_one)
        session.add(dish)
        session.commit()
        session.refresh(dish)

    @staticmethod
    def delete_dish(session: Session, name: str):
        if not name:

            raise ValidationError('Нельзя удалить то, чего нет')

        db_dish = session.query(Dish).filter_by(name=name).first()

        session.delete(db_dish)
        session.commit()

    @staticmethod
    def add_amount(session: Session, data: dict[str, int]):
        name = data.get('name')
        amount = data.get('amount')

        if not name:

            raise ValidationError('Поле названия '
                                  'обязательно для заполнения!')

        if not amount:

            raise ValidationError('Поле количества '
                                  'обязательно для заполнения!')

        try:
            float(amount)

        except ValueError:

            raise ValidationError('Это не число')

        db_type = session.query(RawType).filter_by(name=name).first()

        if raw_amount := (session.query(RawAmount)
                          .filter_by(type=db_type).first()):
            raw_amount.freezer += int(amount)

        else:
            raw_amount = RawAmount(type=db_type,
                                   freezer=int(amount))
            session.add(raw_amount)

        session.commit()

    @staticmethod
    def add_report(session: Session, data: dict[str, int]):
        results = defaultdict(int)

        for name, amount in data.items():
            if not name:

                raise ValidationError('Поле названия обязательно '
                                      'для заполнения!')

            if not amount:

                raise ValidationError(
                    'Поле количества обязательно для заполнения!')

            try:
                float(amount)

            except ValueError:

                raise ValidationError('Это не число')

            dish = (session.query(Dish)
                    .filter_by(name=name).first())

            if raw_amount := (session.query(RawAmount)
                              .filter_by(type=dish.type).first()):
                used_amount = int(amount) * dish.amount
                raw_amount.fridge -= used_amount

                if raw_amount.fridge < 0:

                    session.rollback()
                    raise ValidationError(f'При таком количестве порций '
                                          f'({amount}) количество мяса вида '
                                          f'"{raw_amount.type.name}" станет '
                                          f'отрицательным!')

                results[raw_amount.type.name] += used_amount

        session.commit()

        return results

    @staticmethod
    def freezer_to_fridge(session: Session, data: dict[str, int]):
        name = data.get('name')
        amount = data.get('amount')

        if not name:

            raise ValidationError('Поле названия '
                                  'обязательно для заполнения!')

        if not amount:

            raise ValidationError('Поле количества '
                                  'обязательно для заполнения!')

        try:
            float(amount)

        except ValueError:

            raise ValidationError('Это не число')

        type = session.query(RawType).filter_by(name=name).first()

        if raw_amount := session.query(RawAmount).filter_by(type=type).first():
            raw_amount.freezer -= int(amount)
            raw_amount.fridge += int(amount)

            session.commit()

    @staticmethod
    def fridge_to_freezer(session: Session, data: dict[str, int]):
        name = data.get('name')
        amount = data.get('amount')

        if not name:

            raise ValidationError('Поле названия '
                                  'обязательно для заполнения!')

        if not amount:

            raise ValidationError('Поле количества '
                                  'обязательно для заполнения!')

        try:
            float(amount)

        except ValueError:

            raise ValidationError('Это не число')

        type = session.query(RawType).filter_by(name=name).first()

        if raw_amount := session.query(RawAmount).filter_by(type=type).first():
            raw_amount.fridge -= int(amount)
            raw_amount.freezer += int(amount)

            session.commit()


crud = CRUD()
