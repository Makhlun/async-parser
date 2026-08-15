from bs4 import BeautifulSoup

class Parser:
    
    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find(id="vacancyListId")
        vacancies = container.find_all("li", class_="l-vacancy")

        vacancies_list = []

        for vacancy in vacancies:

            post_date = vacancy.find("div", class_="date")
            if post_date is None:
                continue

            post_date = post_date.get_text(strip=True)

            vacancy_description = vacancy.find("div", class_="title")
            if vacancy_description is None:
                continue

            title_link = vacancy_description.find("a", class_="vt")
            if title_link is None:
                continue
            title = title_link.get_text(strip=True)
            link = title_link.get("href")
            
            company = vacancy_description.find("a", class_="company")
            if company is not None:
                company = company.get_text(strip=True)
            
            salary = vacancy_description.find("span", class_="salary")
            if salary is not None:
                salary = salary.get_text(strip=True)

            location = vacancy_description.find("span", class_="cities")
            if location is not None:
                location = location.get_text(strip=True)
                
            description = vacancy.find("div", class_="sh-info")
            if description is not None:
                description = description.get_text(strip=True)

            vacancy_dict = {
                "post_date":post_date,
                "title":title,
                "description":description,
                "salary":salary,
                "link":link,
                "company":company,
                "location":location
            }

            vacancies_list.append(vacancy_dict)
        return vacancies_list
        