from test import BaseTestCase
from prediction_bot import dailykos


class TestDailyKos(BaseTestCase):
    def test_assemble_tweet_no_changes(self):
        results = {
            'hillary_win_prob': 83.4,
            'trump_win_prob': None,
        }

        changes = {}

        message = dailykos.assemble_tweet_message(results, changes)
        expected = 'Clinton win probability: 83.4%'

        self.assertIn(expected, message)

    def test_assemble_tweet_with_changes(self):
        results = {
            'hillary_win_prob': 83.4,
            'trump_win_prob': None,
        }

        changes = {
            'hillary_win_prob': 0.5,
        }

        message = dailykos.assemble_tweet_message(results, changes)
        expected = 'Clinton win probability: 83.4% (+0.5)'

        self.assertIn(expected, message)

if __name__ == '__main__':
    import unittest
    unittest.main()
