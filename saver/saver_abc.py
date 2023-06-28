import os
from abc import ABC, abstractmethod


class Saver(ABC):
    """Абстрактный класс, задает шаблон классов для сохранения данных в файл"""

    # абсолютный путь из текущего файла к корневой папке проекта
    _ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

    def __init__(self, path_file: tuple) -> None:
        """
        Инициализатор объектов класса
        :param path_file: кортеж, содержащий строки с названием папок и файлов для построения пути к файлу
        """

        self.path_file = os.path.join(self._ROOT_DIR, *path_file)

    @abstractmethod
    def add_vacancies(self, list_vacancies: list) -> None:
        """
        Добавляет больше вакансий в непустой файл

        :param list_vacancies: список с информацией о найденных вакансиях
        """
        pass

    @abstractmethod
    def write_vacancies(self, list_vacancies: list) -> None:
        """
        Перезаписывает (или создает) файл для записи информации о найденных вакансиях

        :param list_vacancies: список с информацией о найденных вакансиях
        """
        pass

    @abstractmethod
    def clean_file(self):
        """Полностью очистить файл с информацией о вакансиях"""
        pass

    @abstractmethod
    def load_vacancies(self) -> list:
        """Загрузить информацию о вакансиях из файла"""
        pass
