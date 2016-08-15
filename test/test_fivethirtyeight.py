from test import BaseTestCase
from prediction_bot import fivethirtyeight


class TestFiveThirtyEight(BaseTestCase):
    def test_assemble_tweet(self):
        results = {
            'hillary_polls_prob': 91.4,
            'trump_polls_prob': 7.3,
            'hillary_plus_prob': 91.4,
            'trump_plus_prob': 7.3,
            'hillary_now_prob': 91.4,
            'trump_now_prob': 7.3,
        }

        changes = {
            'hillary_polls_prob': 0,
            'trump_polls_prob': 0,
            'hillary_plus_prob': 0.5,
            'trump_plus_prob': -0.5,
            'hillary_now_prob': 0,
            'trump_now_prob': 0,
        }

        message = fivethirtyeight.assemble_tweet_message(results, changes)
        expected = 'New @fivethirtyeight forecast data!\n\nPolls: H91.4 | T7.3\nPollsPlus: H91.4 | T7.3 (+0.5H)\nNowCast: H91.4 | T7.3\n\n'

        self.assertEqual(expected, message)

    def test_assemble_tweet_with_changes(self):
        results = {
            'hillary_polls_prob': 91.4,
            'trump_polls_prob': 7.3,
            'hillary_plus_prob': 91.4,
            'trump_plus_prob': 7.3,
            'hillary_now_prob': 91.4,
            'trump_now_prob': 7.3,
        }

        changes = {
            'hillary_polls_prob': 0.5,
            'trump_polls_prob': -0.5,
            'hillary_plus_prob': 0.5,
            'trump_plus_prob': -0.5,
            'hillary_now_prob': 0.5,
            'trump_now_prob': -0.5,
        }

        message = fivethirtyeight.assemble_tweet_message(results, changes)

        self.assertIn('Polls: H91.4 | T7.3 (+0.5H)\n', message)
        self.assertIn('PollsPlus: H91.4 | T7.3 (+0.5H)\n', message)
        self.assertIn('NowCast: H91.4 | T7.3 (+0.5H)\n', message)


if __name__ == '__main__':
    import unittest
    unittest.main()
