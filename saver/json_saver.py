import json

from saver.saver_abc import Saver
from vacancy.vacancy_hh import VacancyHeadHunter
from vacancy.vacancy_sj import VacancySuperJob


class JSONSaver(Saver):

    def add_vacancies(self, list_vacancies: list) -> None:
        """
        Добавляет больше вакансий в непустой файл

        :param list_vacancies: список с информацией о найденных вакансиях
        """

        with open(self.path_file, "r", encoding="utf-8") as json_file:
            try:
                vacancies = json.load(json_file)
            except json.decoder.JSONDecodeError:
                self.write_vacancies(list_vacancies)
                return

        for vacancy in list_vacancies:
            if vacancy not in vacancies:
                vacancies.append(vacancy)

        self.write_vacancies(vacancies)

    def write_vacancies(self, list_vacancies: list) -> None:
        """
        Перезаписывает (или создает) файл для записи информации о найденных вакансиях

        :param list_vacancies: список с информацией о найденных вакансиях
        """

        with open(self.path_file, "w", encoding="utf-8") as json_file:
            json.dump(list_vacancies, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

        print(f"\nВакансии записаны в файл {self.path_file}")

    def clean_file(self) -> None:
        """Полностью очистить файл с информацией о вакансиях"""

        with open(self.path_file, "w", encoding="utf-8") as json_file:
            pass

        print(f"\nИнформация была стёрта из файла {self.path_file} ")

    def load_vacancies(self) -> list:
        """
        Загрузить информацию о вакансиях из файла
        Сразу строит объекты соответствующих классов вакансий
        """

        with open(self.path_file, "r", encoding="utf-8") as json_file:
            vacancies = json.load(json_file)

        list_vacancies = []

        for vacancy in vacancies:
            if "hh.ru" in vacancy.get("url", ""):
                vacancy = VacancyHeadHunter(vacancy)
            elif "superjob.ru" in vacancy.get("link", ""):
                vacancy = VacancySuperJob(vacancy)
            else:
                continue
            list_vacancies.append(vacancy)

        return list_vacancies
