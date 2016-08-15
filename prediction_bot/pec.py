import asyncio
import logging
from prediction_bot.web import get_page
import re
import pprint

from prediction_bot.utils import (
    has_forecast_changed,
    get_forecast_changes,
    change_to_string)
from prediction_bot.db import PEC, database_session
from prediction_bot.twitter_api import post_tweet

POLLS_ONLY_URL = 'http://election.princeton.edu/'
CLINTON_PERCENTAGE_REGEX = 'Clinton Nov. win probability.*Bayesian\s*(.*)%'
TRUMP_PERCENTAGE_REGEX = 'Trump Nov. win probability.*Bayesian\s*(.*)%'


def parse_page(html):
    clinton_search = re.search(CLINTON_PERCENTAGE_REGEX, html)
    trump_search = re.search(TRUMP_PERCENTAGE_REGEX, html)
    is_trump = False

    if not clinton_search and not trump_search:
        raise Exception('Could not find Clinton or Trump data in PEC.')

    if clinton_search:
        search = clinton_search

    if trump_search:
        search = trump_search
        is_trump = True

    try:
        percent = search.group(1)
    except Exception as e:
        logging.error('Could not parse PEC: {}'.format(e))
        raise e

    trump_win_prob = None
    hillary_win_prob = None

    if is_trump:
        trump_win_prob = int(percent)
    else:
        hillary_win_prob = int(percent)

    return dict(
        trump_win_prob=trump_win_prob,
        hillary_win_prob=hillary_win_prob
    )


def save_new_forecast(results):
    logging.info('Saving new PEC results to db.')
    with database_session() as session:
        f = PEC(**results)
        session.add(f)
        session.commit()


def assemble_tweet_message(results, changes):
    logging.info('Assembling tweet message with results: {}'.format(results))
    msg = 'New Princeton Electon Consortium forecast!\n\n'

    if results.get('hillary_win_prob'):
        msg += 'Clinton win probability: {}%\n\n'.format(
            results['hillary_win_prob'])

        if changes.get('hillary_win_prob'):
            msg = msg.strip()
            msg += " {}\n\n".format(
                change_to_string(changes.get('hillary_win_prob')))
    else:
        msg += 'Trump win probability: {}%\n\n'.format(
            results['trump_win_prob'])

        if changes.get('trump_win_prob'):
            msg = msg.strip()
            msg += " {}\n\n".format(
                change_to_string(changes.get('trump_win_prob')))

    msg += '@samwangphd'

    return msg

async def get_pec_page(client):
    html = await get_page(client, POLLS_ONLY_URL)

    return html

async def research(client):
    loop = asyncio.get_event_loop()
    html = await get_pec_page(client)

    results = await loop.run_in_executor(None, parse_page, html)
    logging.info('PEC Results are:\n{}'.format(pprint.pformat(results)))

    is_forecast_new = await loop.run_in_executor(
        None, has_forecast_changed, PEC, results
    )

    if not is_forecast_new:
        logging.info('PEC Forecast has not changed.')
        return

    changes = await loop.run_in_executor(
        None, get_forecast_changes, PEC, results)
    await loop.run_in_executor(None, save_new_forecast, results)

    message = assemble_tweet_message(results, changes)
    await loop.run_in_executor(None, post_tweet, message)
