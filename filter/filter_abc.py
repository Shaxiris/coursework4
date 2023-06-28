from abc import ABC, abstractmethod


class Filter(ABC):
    """
    Абстрактный класс для описания фильтра.
    Фильтр может быть использован при отправке запроса
    и при дальнейшей фильтрации полученных результатов
    """

    _AREA_CODES_URL: str  # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _FILTER_DICTIONARY_URL: str  # ссылка на ресурс, возвращающий словари со значениями для фильтра

    def __init__(self) -> None:
        """
        Инициализатор фильтра. Устанавливает значения фильтра по умолчанию,
        получает и устанавливает некоторые словари с допустимыми значениями, получаемые с сайта
        """
        # в этих полях находятся словари сайта с перечнем допустимых значений фильтра
        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        self.parameters = {}

    def get_all_parameters(self) -> dict:
        """Возвращает все параметры фильтра в формате словаря"""

        return self.parameters

    def get_request_parameters(self) -> dict:
        """Возвращает параметры фильтра, использующиеся при отправке запроса на сайт"""

        request_parameters = {key: value for key, value in self.parameters.items() if value is not None}

        return request_parameters

    @abstractmethod
    def set_request_parameters(self) -> None:
        """Устанавливает параметры фильтра, использующиеся при отправке запроса на сайт"""
        pass

    @abstractmethod
    def get_filtering_parameters(self) -> dict:
        """Возвращает параметры фильтра, использующиеся для фильтрации полученных вакансий"""
        pass

    @abstractmethod
    def set_filtering_parameters(self) -> None:
        """Устанавливает параметры фильтра, использующиеся для фильтрации полученных вакансий"""
        pass

    @abstractmethod
    def compare_parameters(self, vacancy_dict: dict) -> bool:
        """Проверяет вакансию на соответствие установленным значениям фильтра"""
        pass

    @abstractmethod
    def get_filter_dictionary(self) -> dict:
        """Возвращает словарь сайта, содержащий надлежащие значения для фильтра"""
        pass

    @abstractmethod
    def get_areas_info(self) -> dict | list[dict]:
        """
        Возвращает коллекцию, содержащую информацию о городах и регионах,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_areas_names(self) -> list:
        """
        Возвращает список, содержащий города и регионы,
        которые можно указывать для поиска
        """
        pass

    @abstractmethod
    def get_area_id(self, name: str) -> str | int:
        """
        Возвращает id, который кодирует переданный
        функции город или регион
        """
        pass