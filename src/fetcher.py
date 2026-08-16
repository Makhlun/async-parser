import requests
import logging

logger = logging.getLogger(__name__)

class Fetcher:
    HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch(self, url):
        logger.info(f"Fetching url: {url}")
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        logger.info(f"Fetched with {response.status_code} status.")

        return response.text