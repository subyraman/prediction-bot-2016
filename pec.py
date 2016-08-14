import asyncio
import logging
from web import get_page
import re
import json
import pprint

from utils import custom_round, has_forecast_changed
from db import FiveThirtyEight, database_session
from twitter_api import post_tweet

POLLS_ONLY_URL = 'http://projects.fivethirtyeight.com/2016-election-forecast/'
US_REGEX = 'race\.stateData\s*=\s*(\{"state"\s*:\s*"US".*\})'


def get_win_probability(forecast_data, party, forecast):
    return custom_round(
        forecast_data['latest'][party]['models'][forecast]['winprob'], 1)


def parse_page(html):
    return dict(
        hillary_now_prob=hillary_now_prob,
        hillary_plus_prob=hillary_plus_prob,
        hillary_polls_prob=hillary_polls_prob,
        trump_now_prob=trump_now_prob,
        trump_plus_prob=trump_plus_prob,
        trump_polls_prob=trump_polls_prob
    )


def save_new_forecast(results):
    logging.info('Saving new 538 results to db.')
    with database_session() as session:
        f = FiveThirtyEight(**results)
        session.add(f)
        session.commit()


def assemble_tweet_message(results):
    logging.info('Assembling tweet message with results: {}'.format(results))
    msg = 'New 538 Forecast data!\n\n'

    msg += 'Polls: Clinton {} | Trump {}\n'.format(
        results['hillary_polls_prob'], results['trump_polls_prob'])
    msg += 'PollsPlus: Clinton {} | Trump {}\n'.format(
        results['hillary_plus_prob'], results['trump_plus_prob'])
    msg += 'NowCast: Clinton {} | Trump {}\n'.format(
        results['hillary_now_prob'], results['trump_now_prob'])

    return msg

async def get_538_page():
    html = await get_page(POLLS_ONLY_URL)

    return html

async def research():
    loop = asyncio.get_event_loop()
    html = await get_538_page()

    results = await loop.run_in_executor(None, parse_page, html)
    logging.info('538 Results are:\n{}'.format(pprint.pformat(results)))

    is_forecast_new = await loop.run_in_executor(
        None, has_forecast_changed, FiveThirtyEight, results
    )

    if not is_forecast_new:
        logging.info('538 Forecast has not changed.')
        return

    await loop.run_in_executor(None, save_new_forecast, results)

    message = assemble_tweet_message(results)
    await loop.run_in_executor(None, post_tweet, message)
