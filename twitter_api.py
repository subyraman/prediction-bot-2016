import twitter
import os
import logging

api = twitter.Api(
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'].strip(),
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'].strip(),
    access_token_key=os.environ['TWITTER_ACCESS_TOKEN'].strip(),
    access_token_secret=os.environ['TWITTER_ACCESS_SECRET'].strip())


def post_tweet(message):
    logging.info('Posting new tweet: {}'.format(message))
    api.PostUpdate(message, verify_status_length=False)
