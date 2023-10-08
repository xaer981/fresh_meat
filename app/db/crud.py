from sqlalchemy import select
from sqlalchemy.orm import Session

from .exceptions import ValidationError
from .models import CountPerOne, RawAmount, RawType


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

    return (session.query(RawType.name, CountPerOne.amount)
            .select_from(RawType)
            .join(RawType.count_per_one)
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


def add_type(session: Session, data: dict[str, int]):
    name = data.get('name')
    count_per_one = data.get('count_per_one')

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

    count_per_one_obj = CountPerOne(type=new_type,
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
    object = session.query(CountPerOne).filter_by(type_id=type.id).first()

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
        amount = float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.freezer += amount

    else:
        raw_amount = RawAmount(type=type,
                               freezer=amount)
        session.add(raw_amount)

    session.commit()


def freezer_to_fridge(session: Session, data: dict[str, int]):
    name = data.get('name')
    amount = data.get('amount')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not amount:

        raise ValidationError('Поле количества обязательно для заполнения!')

    try:
        amount = float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.freezer -= amount
        raw_amount.fridge += amount

        session.commit()


def fridge_to_freezer(session: Session, data: dict[str, int]):
    name = data.get('name')
    amount = data.get('amount')

    if not name:

        raise ValidationError('Поле названия обязательно для заполнения!')

    if not amount:

        raise ValidationError('Поле количества обязательно для заполнения!')

    try:
        amount = float(amount)

    except ValueError:

        raise ValidationError('Это не число')

    type = session.query(RawType).filter_by(name=name).first()

    if raw_amount := session.query(RawAmount).filter_by(type=type).first():
        raw_amount.fridge -= amount
        raw_amount.freezer += amount

        session.commit()
