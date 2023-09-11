from sqlalchemy.orm import Session

from .models import CountPerOne, RawAmount, RawType


def get_total(session: Session):

    return (session.query(RawType.name, RawAmount.total)
            .select_from(RawAmount)
            .join(RawAmount.type_name)
            .all())


def get_fridge(session: Session):

    return (session.query(RawType.name, RawAmount.fridge)
            .select_from(RawAmount)
            .join(RawAmount.type_name)
            .all())


def get_freezer(session: Session):

    return (session.query(RawType.name, RawAmount.freezer)
            .select_from(RawAmount)
            .join(RawAmount.type_name)
            .all())


def get_types(session: Session):

    return (session.query(RawType.name, CountPerOne.amount)
            .select_from(RawType)
            .join(RawType.count_per_one)
            .all())


def add_type(session: Session, data: tuple[str]):
    print(data)
