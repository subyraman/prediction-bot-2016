from prediction_bot.utils import (
    has_forecast_changed,
    custom_round,
    get_forecast_changes,
    change_to_string
)
from prediction_bot.db import FiveThirtyEight
from test import BaseTestCase


class TestUtils(BaseTestCase):
    default_data = dict(
        hillary_now_prob=88.0,
        trump_now_prob=12.0,
        hillary_plus_prob=88.0,
        trump_plus_prob=12.0,
        hillary_polls_prob=88.0,
        trump_polls_prob=12.0,
    )

    def test_forecast_change_boolean(self):
        f = FiveThirtyEight(**self.default_data)

        self.session.add(f)
        self.session.commit()

        changes = self.default_data

        ret = has_forecast_changed(FiveThirtyEight, changes)
        self.assertFalse(ret)

        changes = dict(self.default_data)
        changes['hillary_now_prob'] = 88.5
        changes['trump_now_prob'] = 11.5

        ret = has_forecast_changed(FiveThirtyEight, changes)
        self.assertTrue(ret)

    def test_get_forecast_changes(self):
        f = FiveThirtyEight(**self.default_data)

        self.session.add(f)
        self.session.commit()

        changes = dict(self.default_data)
        changes['hillary_now_prob'] = 89.0
        changes['trump_now_prob'] = 11.0

        ret = get_forecast_changes(FiveThirtyEight, changes)
        self.assertEqual(len(ret.keys()), 2)
        self.assertEqual(ret['hillary_now_prob'], 1.0)
        self.assertEqual(ret['trump_now_prob'], -1.0)

    def test_change_to_string_positive(self):
        ret = change_to_string(1)
        self.assertEqual(ret, "+1")

    def test_change_to_string_negative(self):
        ret = change_to_string(-1)
        self.assertEqual(ret, "-1")

    def test_custom_round_up(self):
        for num in [7.55, 7.56, 7.57, 7.58, 7.59]:
            ret = custom_round(num, 1)
            self.assertEqual(
                ret, 7.6, '{} should round up'.format(num))

        for num in [7.50, 7.51, 7.52, 7.53, 7.54]:
            ret = custom_round(num, 1)
            self.assertEqual(
                ret, 7.5, '{} should round down'.format(num))


if __name__ == '__main__':
    import unittest
    unittest.main()
