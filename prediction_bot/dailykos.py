

import asyncio
import logging
from prediction_bot.web import get_page
import re
import pprint
import json

from prediction_bot.utils import (
    custom_round,
    has_forecast_changed,
    get_forecast_changes,
    change_to_string)
from prediction_bot.db import DailyKos, database_session
from prediction_bot.twitter_api import post_tweet

URL = 'http://elections.dailykos.com/app/data/assign_forecasts_2016.js'
DAILYKOS_REGEX = 'window.tables.forecasts\s*=\s*(.*)'


def parse_page(html):
    search = re.search(DAILYKOS_REGEX, html)
    try:
        forecast_data = json.loads(search.group(1))
    except Exception as e:
        logging.error('Failed to get parse data out of DailyKos: {}'.format(e))
        raise e

    hillary_win_data = forecast_data['president']['forecast']['data']['democrat_overall_win_probability']
    trump_win_data = None

    hillary_win_prob = None
    if hillary_win_data:
        hillary_win_prob = custom_round(hillary_win_data * 100, 1)

    trump_win_prob = None
    if trump_win_data:
        trump_win_prob = custom_round(trump_win_data * 100, 1)

    return dict(
        trump_win_prob=trump_win_prob,
        hillary_win_prob=hillary_win_prob
    )


def custom_change_to_string(change):
    rounded = custom_round(change, 1)
    return change_to_string(rounded)


def save_new_forecast(results):
    logging.info('Saving new DailyKos results to db.')
    with database_session() as session:
        f = DailyKos(**results)
        session.add(f)
        session.commit()


def assemble_tweet_message(results, changes):
    logging.info('Assembling tweet message with results: {}'.format(results))
    msg = 'New DailyKos forecast!\n\n'

    if results.get('hillary_win_prob'):
        msg += 'Clinton win probability: {}%\n\n'.format(
            results['hillary_win_prob'])

        if changes.get('hillary_win_prob'):
            msg = msg.strip()
            msg += " ({})\n\n".format(
                custom_change_to_string((changes.get('hillary_win_prob'))))
    else:
        msg += 'Trump win probability: {}%\n\n'.format(
            results['trump_win_prob'])

        if changes.get('trump_win_prob'):
            msg = msg.strip()
            msg += " ({})\n\n".format(
                custom_change_to_string((changes.get('trump_win_prob'))))

    msg += '@DKElections'

    return msg

async def get_pec_page(client):
    html = await get_page(client, URL)

    return html

async def research(client):
    loop = asyncio.get_event_loop()
    html = await get_pec_page(client)

    results = await loop.run_in_executor(None, parse_page, html)
    logging.info('DailyKos Results are:\n{}'.format(pprint.pformat(results)))

    is_forecast_new = await loop.run_in_executor(
        None, has_forecast_changed, DailyKos, results
    )

    if not is_forecast_new:
        logging.info('DailyKos Forecast has not changed.')
        return

    changes = await loop.run_in_executor(
        None, get_forecast_changes, DailyKos, results)
    await loop.run_in_executor(None, save_new_forecast, results)

    message = assemble_tweet_message(results, changes)
    await loop.run_in_executor(None, post_tweet, message)
