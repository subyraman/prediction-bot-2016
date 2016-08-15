import asyncio
import logging
from prediction_bot.web import get_page
import re
import json
import pprint

from prediction_bot.utils import custom_round, has_forecast_changed, get_forecast_changes, change_to_string
from prediction_bot.db import FiveThirtyEight, database_session
from prediction_bot.twitter_api import post_tweet

POLLS_ONLY_URL = 'http://projects.fivethirtyeight.com/2016-election-forecast/'
US_REGEX = 'race\.stateData\s*=\s*(\{"state"\s*:\s*"US".*\})'


def get_win_probability(forecast_data, party, forecast):
    return custom_round(
        forecast_data['latest'][party]['models'][forecast]['winprob'], 1)


def parse_page(html):
    search = re.search(US_REGEX, html)  

    try:
        forecast_data = json.loads(search.group(1))
    except Exception as e:
        logging.error('Failed to get parse data out of 538: {}'.format(e))
        raise Exception

    hillary_now_prob = get_win_probability(forecast_data, 'D', 'now')
    hillary_plus_prob = get_win_probability(forecast_data, 'D', 'plus')
    hillary_polls_prob = get_win_probability(forecast_data, 'D', 'polls')
    trump_now_prob = get_win_probability(forecast_data, 'R', 'now')
    trump_plus_prob = get_win_probability(forecast_data, 'R', 'plus')
    trump_polls_prob = get_win_probability(forecast_data, 'R', 'polls')

    return dict(
        hillary_now_prob=hillary_now_prob,
        hillary_plus_prob=hillary_plus_prob,
        hillary_polls_prob=hillary_polls_prob,
        trump_now_prob=trump_now_prob,
        trump_plus_prob=trump_plus_prob,
        trump_polls_prob=trump_polls_prob
    )

def custom_change_to_string(change):
    rounded = custom_round(change, 1)
    return change_to_string(rounded)

def save_new_forecast(results):
    logging.info('Saving new 538 results to db.')
    with database_session() as session:
        f = FiveThirtyEight(**results)
        session.add(f)
        session.commit()


def assemble_tweet_message(results, changes):
    logging.info('Assembling tweet message with results: {}'.format(results))
    msg = 'New @fivethirtyeight forecast data!\n\n'

    msg += 'Polls: H{} | T{}\n'.format(
        results['hillary_polls_prob'],
        results['trump_polls_prob'])

    if changes.get('hillary_polls_prob'):
        msg = msg.strip()
        msg += ' ({}H)\n'.format(
            custom_change_to_string(changes.get('hillary_polls_prob')))

    msg += 'PollsPlus: H{} | T{}\n'.format(
        results['hillary_plus_prob'], results['trump_plus_prob'])

    if changes.get('hillary_plus_prob'):
        msg = msg.strip()
        msg += ' ({}H)\n'.format(
            custom_change_to_string(
                changes.get('hillary_plus_prob')))

    msg += 'NowCast: H{} | T{}\n\n'.format(
        results['hillary_now_prob'], results['trump_now_prob'])

    if changes.get('hillary_now_prob'):
        msg = msg.strip()
        msg += ' ({}H)\n'.format(
            custom_change_to_string(changes.get('hillary_now_prob')))

    return msg

async def get_538_page(client):
    html = await get_page(client, POLLS_ONLY_URL)

    return html

async def research(client):
    loop = asyncio.get_event_loop()
    html = await get_538_page(client)

    results = await loop.run_in_executor(None, parse_page, html)
    logging.info('538 Results are:\n{}'.format(pprint.pformat(results)))

    is_forecast_new = await loop.run_in_executor(
        None, has_forecast_changed, FiveThirtyEight, results
    )

    if not is_forecast_new:
        logging.info('538 Forecast has not changed.')
        return

    changes = await loop.run_in_executor(
        None, get_forecast_changes, FiveThirtyEight, results)
    await loop.run_in_executor(None, save_new_forecast, results)

    message = assemble_tweet_message(results, changes)
    await loop.run_in_executor(None, post_tweet, message)
