from bs4 import BeautifulSoup

with open("data/sample.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
container = soup.find(id="vacancyListId")
vacancies = container.find_all("li", class_="l-vacancy")

for vacancy in vacancies:
    post_date = vacancy.find("div", class_="date").get_text(strip=True)
    vacancy_description = vacancy.find("div", class_="title")
    title = vacancy_description.find("a", class_="vt").get_text(strip=True)
    link = vacancy_description.find("a", class_="vt").get("href")
    company = vacancy_description.find("a", class_="company").get_text(strip=True)
    location = vacancy_description.find("span", class_="cities").get_text(strip=True)
    description = vacancy.find("div", class_="sh-info").get_text(strip=True)
    

