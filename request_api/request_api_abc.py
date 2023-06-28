from abc import ABC, abstractmethod


class API(ABC):
    """
    Абстрактный класс для отправки запросов на сайт с вакансиями
    и получения списка вакансий в соответствии с заданными параметрами
    """

    _URL = None  # ссылка на сайт для запроса вакансий
    _MAX_QUANTITY = 500  # максимальное допустимое запрашиваемое количество вакансий

    def __init__(self, request_filter, quantity=10) -> None:
        """
        Инициализатор для объектов класса

        :param request_filter: объект какого-то из класса фильтров
        :param quantity: желаемое количество вакансий
        """

        self.request_filter = request_filter
        self.quantity = quantity

    @property
    def request_filter(self):
        return self._request_filter

    @request_filter.setter
    def request_filter(self, value):
        self._request_filter = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        """
        Сеттер для указания количества запрошенных вакансий

        Проверки:
            представлено ли значение в формате int
            попадает ли в диапазон [0, 500]

        Если нет, устанавливает значение по умолчанию
        """

        if type(value) is int and 0 <= value < 500:
            self._quantity = value
        else:
            self._quantity = 10
            print("\nНе соблюдены условия указания количества вакансий:\n"
                  "Количество должно быть выражено целым неотрицательным числом\n"
                  "и не превышать максимальное возможное значение = 500\n"
                  "Установлен параметр по умолчанию = 10")

    def get_parameters(self) -> dict:
        """Возвращает установленные параметры фильтра"""

        return self.request_filter.get_request_parameters()

    @abstractmethod
    def get_info(self) -> list[dict]:
        """Возвращает ответ на запрос, отправленный на сайт с вакансиями"""
        pass

    @abstractmethod
    def get_vacancies(self) -> list[dict]:
        """Возвращает список вакансий в заданном количестве, если это возможно"""
        pass
