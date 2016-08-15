from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
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

import sys
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

    def get_forecast_changes(self, new_data):
        ret = {}

        for key, value in new_data.items():
            old_value = getattr(self, key)
            if old_value != value:
                if type(old_value) == type(value):
                    ret[key] = value - old_value

        return ret

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


class PEC(Base):
    __tablename__ = 'pec'

    hillary_win_prob = Column(Integer)
    trump_win_prob = Column(Integer)


if 'test' in sys.argv[0]:
    database_url = 'sqlite:////:memory:'
else:
    database_url = os.environ['DATABASE_URL']

logging.info('Database URL is {}'.format(database_url))

engine = create_engine(database_url)
Session = scoped_session(sessionmaker(bind=engine))


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
        Session.remove()
