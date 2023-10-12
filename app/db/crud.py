from sqlalchemy import select
from sqlalchemy.orm import Session

from .exceptions import ValidationError
from .models import Dish, RawAmount, RawType


def get_total(session: Session):

    return (session.query(RawType.name, RawAmount.total)
            .select_from(RawAmount)
            .join(RawAmount.type)
            .all())


def get_fridge(session: Session):

    return (session.query(RawType.name, RawAmount.fridge)
            .select_from(RawAmount)
            .join(RawAmount.type)
            .all())


def get_freezer(session: Session):

    return (session.query(RawType.name, RawAmount.freezer)
            .select_from(RawAmount)
            .join(RawAmount.type)
            .all())


def get_types(session: Session):

    return session.query(RawType.name).all()


def get_dishes(session: Session):

    return (session.query(RawType.name, Dish.amount)
            .select_from(RawType)
            .join(RawType.dishes)
            .all())


def get_types_names(session: Session):

    return session.execute(select(RawType.name)).scalars().all()


def get_type_freezer(session: Session, name: str):
    type = session.query(RawType).filter_by(name=name).first()

    return session.execute(select(RawAmount.freezer)
                           .where(RawAmount.type == type)).scalar()


def get_type_fridge(session: Session, name: str):
    type = session.query(RawType).filter_by(name=name).first()

    return session.execute(select(RawAmount.fridge)
                           .where(RawAmount.type == type)).scalar()


def add_type(session: Session, name: str):
    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    new_type = RawType(name=name)

    session.add(new_type)
    session.commit()


def add_dish(session: Session, data: dict[str, int]):
    name = data.get('name')
    count_per_one = data.get('count_per_one')
    # dish_name = data.get('dish_name')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not count_per_one:

        raise ValidationError('Поле количества на порцию '
                              'обязательно для заполнения!')

    try:
        float(count_per_one)

    except ValueError:

        raise ValidationError('Это не число')

    new_type = RawType(name=name)
    session.add(new_type)

    count_per_one_obj = Dish(type=new_type,
                             amount=int(count_per_one))
    session.add(count_per_one_obj)

    session.commit()


def update_type(session: Session, data: dict[str, int]):
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

    type = session.query(RawType).filter_by(name=name).first()
    object = session.query(Dish).filter_by(type_id=type.id).first()

    object.amount = int(count_per_one)
    session.add(object)
    session.commit()
    session.refresh(object)


def add_amount(session: Session, data: dict[str, int]):
    name = data.get('name')
    amount = data.get('amount')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not amount:

        raise ValidationError('Поле количества обязательно для заполнения!')

    try:
        float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.freezer += int(amount)

    else:
        raw_amount = RawAmount(type=type,
                               freezer=int(amount))
        session.add(raw_amount)

    session.commit()


def add_report(session: Session, data: dict[str, int]):
    results = {}

    for name, amount in data.items():
        if not name:

            raise ValidationError('Поле названия обязательно для заполнения!')

        if not amount:

            raise ValidationError(
                'Поле количества обязательно для заполнения!')

        try:
            float(amount)

        except ValueError:

            raise ValidationError('Это не число')

        db_type = session.query(RawType).filter_by(name=name).first()
        count_per_one = (session.query(Dish)
                         .filter_by(type=db_type).first())

        if db_type is None:

            raise ValidationError(f'Вида с названием {name} не существует')

        if raw_amount := (session.query(RawAmount)
                          .filter_by(type=db_type).first()):
            used_amount = int(amount) * count_per_one.amount
            raw_amount.fridge -= used_amount

            if raw_amount.fridge < 0:

                session.rollback()
                raise ValidationError(f'При таком количестве порций '
                                      f'({amount}) количество мяса вида '
                                      f'"{db_type.name}" станет '
                                      f'отрицательным!')

            results[db_type.name] = used_amount

    session.commit()

    return results


def freezer_to_fridge(session: Session, data: dict[str, int]):
    name = data.get('name')
    amount = data.get('amount')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not amount:

        raise ValidationError('Поле количества обязательно для заполнения!')

    try:
        float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.freezer -= int(amount)
        raw_amount.fridge += int(amount)

        session.commit()


def fridge_to_freezer(session: Session, data: dict[str, int]):
    name = data.get('name')
    amount = data.get('amount')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not amount:

        raise ValidationError('Поле количества обязательно для заполнения!')

    try:
        float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.fridge -= int(amount)
        raw_amount.freezer += int(amount)

        session.commit()
