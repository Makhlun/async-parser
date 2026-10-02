import requests
HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://jobs.dou.ua/vacancies/",
        }

with requests.Session() as session:
    response = session.get("https://jobs.dou.ua/vacancies/", headers=HEADERS)
    response.raise_for_status()
    print(response.status_code)
    print(session.cookies.get_dict())
    csrftoken = session.cookies.get_dict()['csrftoken']

    load_dict = {'csrfmiddlewaretoken':csrftoken, 'count':6000}

    response = session.post("https://jobs.dou.ua/vacancies/xhr-load/", 
                            headers=HEADERS, 
                            data=load_dict)
    response.raise_for_status()
    print(response.json())
