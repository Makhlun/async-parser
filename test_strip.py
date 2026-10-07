from urllib.parse import urlsplit

link = urlsplit("https://jobs.dou.ua/companies/applyft/vacancies/367068/?from=list_hot")

print("list_hot" in link.query)
