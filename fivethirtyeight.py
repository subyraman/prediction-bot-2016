import asyncio
import logging
from web import get_page
import re
import json
import pprint

POLLS_ONLY_URL = 'http://projects.fivethirtyeight.com/2016-election-forecast/'
US_REGEX = 'race\.stateData\s*=\s*(\{"state"\s*:\s*"US".*\})'


def get_win_probability(forecast_data, party, forecast):
    return round(
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

async def get_538_page():
    html = await get_page(POLLS_ONLY_URL)

    return html

async def research():
    loop = asyncio.get_event_loop()
    html = await get_538_page()

    results = await loop.run_in_executor(None, parse_page, html)

    logging.info('538 Results are:\n{}'.format(pprint.pformat(results)))
