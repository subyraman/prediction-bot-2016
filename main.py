import asyncio

from db import Base, engine
from fivethirtyeight import research as fivethirtyeight_research
from pec import research as pec_research
from nyt import research as nyt_research
import logging
import sys

UPDATE_INTERVAL = 300

async def main():
    while True:
        logging.info('Starting research process...')
        await asyncio.gather(
            nyt_research(),
            fivethirtyeight_research(),
            pec_research(),
            return_exceptions=True
        )

        logging.info(
            'Research process finished, sleeping for {} seconds\n\n\n'.format(
                UPDATE_INTERVAL))
        for i in range(5):
            logging.info('...')

        await asyncio.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    root.addHandler(handler)

    Base.metadata.create_all(engine)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
