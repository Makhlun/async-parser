from fetcher import Fetcher
from parser import Parser
from storage import Storage
import logging
import sys
import asyncio
import time

URL = "https://jobs.dou.ua/vacancies/"
DB_PATH = "./data/vacancies.db"

logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
logger = logging.getLogger(__name__)
logger.info("Start Running.")

async def main():
    try:
        start = time.perf_counter()
        data = await fetcher.fetch(url=URL)
        end = time.perf_counter()
        logger.info(f"Fetching took {(end-start):.2f} seconds.")
        parsed_data = []
        for fragment in data:
            parsed_fragment = parser.parse(fragment)
            parsed_data.extend(parsed_fragment)
        storage.save(parsed_data, DB_PATH)
    except Exception as e:
        logger.exception(f"Run failed: {e}")
        sys.exit(1)

fetcher = Fetcher()
parser = Parser()
storage = Storage()

asyncio.run(main())
