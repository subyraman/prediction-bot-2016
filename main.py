import asyncio


import aiohttp
from db import Base, engine
from fivethirtyeight import research as fivethirtyeight_research
from pec import research as pec_research
from nyt import research as nyt_research
import logging
import sys
from twitter_api import api

UPDATE_INTERVAL = 300

async def main():
    with aiohttp.ClientSession() as client:
        while True:
            logging.info('Starting research process...')
            await asyncio.gather(
                nyt_research(client),
                fivethirtyeight_research(client),
                pec_research(client),
            )

            logging.info(
                'Research process finished, sleeping for {} seconds\n\n\n'.format(
                    UPDATE_INTERVAL))
            for i in range(5):
                logging.info('...')

            await asyncio.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    api.VerifyCredentials()

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    root.addHandler(handler)

    Base.metadata.create_all(engine)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
