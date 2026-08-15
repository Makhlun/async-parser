from fetcher import Fetcher
from parser import Parser
from storage import Storage

URL = "https://jobs.dou.ua/vacancies/"
STORAGE_PATH = "./data/output.csv"

fetcher = Fetcher()
parser = Parser()
storage = Storage()

data = fetcher.fetch(url=URL)

parsed_data = parser.parse(data)
storage.save(parsed_data, STORAGE_PATH)
