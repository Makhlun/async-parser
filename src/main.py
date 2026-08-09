from fetcher import Fetcher

url = "https://jobs.dou.ua/vacancies/"

fetcher = Fetcher()
data = fetcher.fetch(url=url)

print(data[:500])