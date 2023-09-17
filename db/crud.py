from sqlalchemy import select
from sqlalchemy.orm import Session

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


def add_type(session: Session, data: dict[str, int]):
    new_type = RawType(name=data.get('name'))
    session.add(new_type)

    count_per_one = CountPerOne(type=new_type,
                                amount=data.get('count_per_one'))
    session.add(count_per_one)

    session.commit()


def add_amount(session: Session, data: dict[str, int]):
    print(data)
