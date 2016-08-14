from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Sequence,
    Float,
    create_engine
)

import os
import datetime
from contextlib import contextmanager
import logging


class Model:
    __abstract__ = True

    id = Column("id", Integer, primary_key=True)
    date_added = Column(DateTime, default=datetime.datetime.now)

    def has_forecast_changed(self, new_data):
        for key, value in new_data.items():
            if getattr(self, key) != value:
                logging.info('{} in {} has changed'.format(
                    key, self.__tablename__))
                return True

        return False

Base = declarative_base(cls=Model)


class FiveThirtyEight(Base):
    __tablename__ = 'fivethirtyeight'

    hillary_now_prob = Column(Float)
    hillary_plus_prob = Column(Float)
    hillary_polls_prob = Column(Float)
    trump_now_prob = Column(Float)
    trump_plus_prob = Column(Float)
    trump_polls_prob = Column(Float)


class NYTUpshot(Base):
    __tablename__ = 'nytupshot'

    hillary_win_prob = Column(Integer)
    trump_win_prob = Column(Integer)
    date_added = Column(DateTime, default=datetime.datetime.now)


class PEC(Base):
    __tablename__ = 'pec'

    hillary_win_prob = Column(Integer)
    trump_win_prob = Column(Integer)
    date_added = Column(DateTime, default=datetime.datetime.now)

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)


@contextmanager
def database_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()