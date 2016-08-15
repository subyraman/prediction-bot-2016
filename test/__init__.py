from unittest import TestCase
from prediction_bot.db import engine, Session, Base


class BaseTestCase(TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()
        Session.remove()
        Base.metadata.drop_all(bind=engine)
