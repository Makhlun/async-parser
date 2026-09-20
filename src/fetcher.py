import requests
import logging
import decorators

logger = logging.getLogger(__name__)

class Fetcher:
    HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://jobs.dou.ua/vacancies/",

        }
    MAX_PAGES = 5
    def __init__(self):
        self.session = requests.Session()



    def fetch(self, url):

        logger.info(f"Fetching url: {url}")

        response = self.session.get(url, headers=self.HEADERS, timeout=10)
        response.raise_for_status()
        logger.info(f"Fetched with {response.status_code} status.")

        token = self.session.cookies.get_dict()['csrftoken']
        offset = 0

        result = []

        for _ in range(self.MAX_PAGES):
            response_json = self._load(url, token, offset)
            result.append(response_json['html'])
            offset += response_json['num']
            logger.info(f"Fetched {offset} records.")

            if response_json['last']:
                return result

        logger.warning(f"Reached limit of page load. Fetched {offset} records.")
        return result

    @decorators.retry()
    @decorators.rate_limit()
    def _load(self, url, token, count):
        load_dict = {'csrfmiddlewaretoken': token, 'count':count}
        response = self.session.post(f"{url}xhr-load/", 
                                        headers=self.HEADERS, 
                                        data=load_dict)
        response.raise_for_status()
        
        response_json = response.json()

        return response_json