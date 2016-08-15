import asyncio
import logging
from web import get_page
import pprint
from bs4 import BeautifulSoup

from utils import has_forecast_changed, get_forecast_changes, change_to_string
from db import NYTUpshot, database_session
from twitter_api import post_tweet

URL = 'http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html'


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    try:
        clinton_percentage = soup.select(
            '.g-cand-top-line-est.clinton-est')[0].text.replace('%', '')
        trump_percentage = soup.select(
            '.g-cand-top-line-est.trump-est')[0].text.replace('%', '')
    except Exception as e:
        logging.error('Could not parse NYTUpshot: {}'.format(e))
        raise Exception

    trump_win_prob = None
    hillary_win_prob = None

    trump_win_prob = int(trump_percentage)
    hillary_win_prob = int(clinton_percentage)

    return dict(
        trump_win_prob=trump_win_prob,
        hillary_win_prob=hillary_win_prob
    )


def save_new_forecast(results):
    logging.info('Saving new NYTUpshot results to db.')
    with database_session() as session:
        f = NYTUpshot(**results)
        session.add(f)
        session.commit()


def assemble_tweet_message(results, changes):
    logging.info('Assembling tweet message with results: {}'.format(results))
    msg = 'Updated New York Times Upshot forecast!\n\n'

    msg += 'Clinton win probability: {}%\n'.format(
        results['hillary_win_prob'])

    if changes.get('hillary_win_prob'):
        msg.strip()
        msg += '{}\n'.format(
            change_to_string(changes['hillary_win_prob']))

    msg += 'Trump win probability: {}%\n'.format(
        results['trump_win_prob'])

    if changes.get('trump_win_prob'):
        msg.strip()
        msg += '{}\n'.format(
            change_to_string(changes['trump_win_prob']))

    msg += '@nytimes'

    return msg

async def get_nytupshot_page():
    html = await get_page(URL)

    return html

async def research():
    loop = asyncio.get_event_loop()
    html = await get_nytupshot_page()

    results = await loop.run_in_executor(None, parse_page, html)
    logging.info('NYTUpshot Results are:\n{}'.format(pprint.pformat(results)))

    is_forecast_new = await loop.run_in_executor(
        None, has_forecast_changed, NYTUpshot, results
    )

    if not is_forecast_new:
        logging.info('NYTUpshot Forecast has not changed.')
        return

    changes = await loop.run_in_executor(
        None, get_forecast_changes, NYTUpshot, results)
    await loop.run_in_executor(None, save_new_forecast, results)

    message = assemble_tweet_message(results, changes)
    await loop.run_in_executor(None, post_tweet, message)
