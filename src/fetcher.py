import asyncio

import aiohttp
import logging
import decorators

logger = logging.getLogger(__name__)

class Fetcher:
    HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://jobs.dou.ua/vacancies/",

        }
    MAX_PAGES = 1000
    TIMEOUT = 10
    WAVE_PAGES = 5
    PAGE_SIZE = 40


    async def fetch(self, url):
        async with aiohttp.ClientSession() as self.session:
            logger.info(f"Fetching url: {url}")

            async with self.session.get(url, headers=self.HEADERS, timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)) as response:
                response.raise_for_status()
                logger.info(f"Fetched with {response.status} status.")
                token = response.cookies['csrftoken'].value
            result = []

            
            for page in range(0, self.MAX_PAGES, self.WAVE_PAGES):
                loads = [self._load(url, token, page_extract*self.PAGE_SIZE) 
                                for page_extract 
                                in range(page, min(page+self.WAVE_PAGES, self.MAX_PAGES))
                    ]
                response_json_set = await asyncio.gather(*loads)
                
                response_json_html = [response_json.get('html', '')
                                for response_json 
                                in response_json_set]
                response_json_last = [response_json.get('last') 
                                for response_json 
                                in response_json_set]
                result.extend(filter(None,response_json_html))

                if (True in response_json_last) or ('' in response_json_html):
                    logger.info(f"Reached last record. Fetched {len(result)} pages.")
                    return result
                
                logger.info(f"Fetched {len(result)} pages.")

            logger.warning(f"Reached limit of page load. Fetched {len(result)} pages.")
            return result

    @decorators.retry()
    @decorators.limit_concurrency()
    async def _load(self, url, token, count):
        load_dict = {'csrfmiddlewaretoken': token, 'count':count}
        response = await self.session.post(f"{url}xhr-load/", 
                                        headers=self.HEADERS, 
                                        data=load_dict)
        response.raise_for_status()
        
        response_json = await response.json()

        return response_json