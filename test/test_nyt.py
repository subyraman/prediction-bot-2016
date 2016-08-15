from test import BaseTestCase
from prediction_bot import nyt


class TestNYT(BaseTestCase):
    def test_parsing_page(self):
        html = """
            <div>
                <div class="g-cand-top-line-est clinton-est">88%</div>
                <div class="g-cand-top-line-est trump-est">12%</div>
            </div>
        """

        results = nyt.parse_page(html)
        self.assertEqual(results['hillary_win_prob'], 88)
        self.assertEqual(results['trump_win_prob'], 12)

    def test_assemble_tweet(self):
        results = {
            'hillary_win_prob': 88,
            'trump_win_prob': 12
        }

        message = nyt.assemble_tweet_message(results, {})

        self.assertIn('Upshot forecast!\n\n', message)
        self.assertIn('Clinton win probability: 88%\n', message)
        self.assertIn('Trump win probability: 12%\n', message)

    def test_assemble_tweet_with_changes(self):
        results = {
            'hillary_win_prob': 88,
            'trump_win_prob': 12
        }

        changes = {
            'hillary_win_prob': 1,
            'trump_win_prob': -1
        }

        message = nyt.assemble_tweet_message(results, changes)

        self.assertIn('Clinton win probability: 88% (+1)\n', message)
        self.assertIn('Trump win probability: 12% (-1)\n', message)

if __name__ == '__main__':
    import unittest
    unittest.main()
