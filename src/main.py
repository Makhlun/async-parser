from fetcher import Fetcher

url = "https://jobs.dou.ua/vacancies/"

fetcher = Fetcher()
data = fetcher.fetch(url=url)

open("data/sample.html", "w", encoding="utf-8").write(data)

with open("data/sample.html", encoding="utf-8") as f:
    html = f.read()
