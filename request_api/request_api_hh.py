import requests
import json

from types import NoneType

from sources.headhunter import urls_hh
from filter.filter_hh import FilterHH
from request_api.request_api_abc import API


class HeadHunterAPI(API):
    """
    Класс для отправки запросов на сайт с вакансиями HeadHunter
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = urls_hh.VACANCIES  # ссылка на сайт для запроса вакансий

    @property
    def request_filter(self) -> FilterHH:
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value: FilterHH) -> None:
        """Установка фильтра, после проверки на принадлежность к подходящему классу"""

        if isinstance(value, (FilterHH, NoneType)):
            self._request_filter = value

    def get_info(self) -> dict:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""

        parameters = self.request_filter.get_request_parameters()

        with requests.get(self._URL, parameters) as request:
            response = request.content.decode("utf-8")
            response = json.loads(response)

        return response

    def get_vacancies(self) -> list:
        """Возвращает список вакансий в заданном количестве, если это возможно"""

        vacancies = []

        print("\nПодождите, ищу запрошенные вакансии...")

        info = self.get_info()
        if info.get('found', 0) == 0:
            print("\nНе найдено вакансий с заданными параметрами.")
            return vacancies

        vacancies.extend(self.get_info().get('items'))
        while len(vacancies) < self.quantity:
            if self.request_filter.parameters["page"] == info.get('pages', 0):
                break

            self.request_filter.parameters["page"] += 1
            vacancies.extend(self.get_info().get('items'))

        print(f"\nНайдено {len(vacancies[:self.quantity])} вакансий.\n"
              f"Всего на сайте по заданным параметрам есть {info.get('found', 0)} вакансий.")

        return vacancies[:self.quantity]