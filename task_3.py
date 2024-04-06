import requests
from bs4 import BeautifulSoup
import re
import json
import datetime


def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            result = old_function(*args, **kwargs)
            with open(path, 'a') as file:
                file.write(
                    f"{datetime.datetime.now()} - вызвана функция «{old_function.__name__}» "
                    f"с аргументами «{args, kwargs}». Значение функции: {result}\n")
            return result
        return new_function
    return __logger


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}


@logger('scraping.log')
def get_html(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    vacancy_links = soup.find_all('a', attrs={'href': re.compile('https://spb.hh.ru/vacancy/')})
    return vacancy_links


@logger('scraping.log')
def get_vacancies(vacancy_links):
    vacancies_list = []

    for link in vacancy_links:
        vacancy_link = link.get('href')
        response = requests.get(vacancy_link, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        if soup.find('div', attrs={'class': 'vacancy-description'}):
            vacancy_description = soup.find('div', attrs={'data-qa': 'vacancy-description'}).text

            if 'Django' or 'Flask' in vacancy_description:
                vacancy = {}

                vacancy['company_name'] = soup.find('a', attrs={'data-qa': 'vacancy-company-name'}).text.strip()
                if soup.find('div', attrs={'data-qa': 'vacancy-salary'}):
                    vacancy['salary'] = soup.find('div', attrs={'data-qa': 'vacancy-salary'}).text.strip()
                else:
                    vacancy['salary'] = 'не указана'
                if soup.find('span', attrs={'data-qa': 'vacancy-view-raw-address'}):
                    vacancy['city'] = soup.find('span', attrs={'data-qa': 'vacancy-view-raw-address'}).text.split(',')[0]
                else:
                    vacancy['city'] = 'не указан'
                vacancy['vacancy_link'] = vacancy_link

                vacancies_list.append(vacancy)
        else:
            print('Нет описания вакансии')

    return json.dumps(vacancies_list)


vacancy_links = get_html('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2')
get_vacancies(vacancy_links)
