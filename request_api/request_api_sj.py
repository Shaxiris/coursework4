import requests
import json

from types import NoneType

from sources.superjob import personal_data
from sources.superjob import urls_sj
from filter.filter_sj import FilterSJ
from request_api.request_api_abc import API


class SuperJobAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями SuperJob
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_sj.VACANCIES  # ссылка на сайт для запроса вакансий

    @property
    def request_filter(self) -> FilterSJ | None:
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value: FilterSJ | None) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterSJ, NoneType)):
            self._request_filter = value

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.request_filter.get_request_parameters()
        headers = {"User-Agent": personal_data.USER_AGENT,
                   "X-Api-App-Id": personal_data.CLIENT_SECRET}

        with requests.get(self._URL, parameters, headers=headers) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        total_vacancies = self.get_info().get('total')
        if total_vacancies == 0:
            print("\nНе найдено вакансий с заданными параметрами.")
            return vacancies

        is_divided_entirely = total_vacancies % self.request_filter.parameters["count"] == 0
        last_page = total_vacancies // self.request_filter.parameters["count"] - is_divided_entirely

        vacancies.extend(self.get_info().get('objects'))

        while len(vacancies) < self.quantity:
            if self.request_filter.parameters["page"] == last_page:
                break

            self.request_filter.parameters["page"] += 1
            vacancies.extend(self.get_info().get('objects'))

        found_vacancies = vacancies[:self.quantity]
        total_vacancies = max((len(found_vacancies), total_vacancies))

        print(f"\nНайдено {len(found_vacancies)} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {total_vacancies} вакансий.")

        return found_vacancies