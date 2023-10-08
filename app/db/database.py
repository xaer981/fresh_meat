from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker


class PreBase:

    @declared_attr
    def __tablename__(self):

        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


engine = create_engine('sqlite:///sqlite.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(cls=PreBase)


def create_db():
    Base.metadata.create_all(engine)
