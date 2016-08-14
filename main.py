import asyncio

from db import Base, engine
from fivethirtyeight import research as fivethirtyeight_research
import logging
import sys

UPDATE_INTERVAL = 10

async def main():
    while True:
        logging.info('Starting research process...')
        await asyncio.gather(fivethirtyeight_research())

        logging.info(
            'Research process finished, sleeping for {} seconds'.format(
                UPDATE_INTERVAL))
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
