from unittest import TestCase
from prediction_bot import pec


class TestPEC(TestCase):
    clinton_html = """
        <li>
            Clinton Nov. win probability: random drift 75%, <a href="/2012/09/29/the-short-term-presidential-predictor/">Bayesian 88%</a>
        </li>
    """

    trump_html = """
        <li>
            Trump Nov. win probability: random drift 75%, <a href="/2012/09/29/the-short-term-presidential-predictor/">Bayesian 12%</a>
        </li>
    """

    results = {
        'hillary_win_prob': 88,
        'trump_win_prob': None
    }

    def test_parsing_clinton_html(self):
        ret = pec.parse_page(self.clinton_html)
        self.assertEqual(ret['hillary_win_prob'], 88)
        self.assertEqual(ret['trump_win_prob'], None)

    def test_parsing_trump_html(self):
        ret = pec.parse_page(self.trump_html)
        self.assertEqual(ret['trump_win_prob'], 12)
        self.assertEqual(ret['hillary_win_prob'], None)

    def test_assemble_tweet_no_changes(self):
        ret = pec.assemble_tweet_message(self.results, {})
        expected = 'New Princeton Electon Consortium forecast!\n\nClinton win probability: 88%\n\n@samwangphd'

        self.assertEqual(ret, expected)

    def test_assemble_tweet_with_changes(self):
        changes = {
            'hillary_win_prob': 1
        }
        ret = pec.assemble_tweet_message(self.results, changes)
        expected = 'New Princeton Electon Consortium forecast!\n\nClinton win probability: 88% (+1)\n\n@samwangphd'
        self.assertEqual(expected, ret)

if __name__ == '__main__':
    import unittest
    unittest.main()
