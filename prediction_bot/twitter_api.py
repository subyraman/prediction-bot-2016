import twitter
import os
import logging
from unittest.mock import MagicMock
import sys

if 'test' not in sys.argv[0]:
    api = twitter.Api(
        consumer_key=os.environ['TWITTER_CONSUMER_KEY'].strip(),
        consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'].strip(),
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN'].strip(),
        access_token_secret=os.environ['TWITTER_ACCESS_SECRET'].strip())
else:
    api = MagicMock()


def post_tweet(message):
    logging.info('Posting new tweet: {}'.format(message))
    api.PostUpdate(message, verify_status_length=False)
