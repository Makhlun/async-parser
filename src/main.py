from fetcher import Fetcher
from parser import Parser
from storage import Storage
import logging

URL = "https://jobs.dou.ua/vacancies/"
STORAGE_PATH = "./data/output.csv"

logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
logger = logging.getLogger(__name__)
logger.info("Start Running.")

fetcher = Fetcher()
parser = Parser()
storage = Storage()

data = fetcher.fetch(url=URL)

parsed_data = parser.parse(data)
storage.save(parsed_data, STORAGE_PATH)
