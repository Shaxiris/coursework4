import requests
import jsonpath_ng as jp

from sources.superjob import urls_sj
from tools.utils import i_input, get_binary_answer
from filter.filter_abc import Filter


class FilterSJ(Filter):
    """
    Класс для настройки фильтра запроса на сайт SuperJob
    и последующей фильтрации полученных вакансий
    """

    # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _AREA_CODES = urls_sj.AREA_CODES
    # ссылка на ресурс, возвращающий словари со значениями для фильтра
    _FILTER_DICTIONARY = urls_sj.FILTER_DICTIONARY

    def __init__(self) -> None:
        """
        Инициализатор фильтра. Устанавливает значения фильтра по умолчанию,
        получает и устанавливает некоторые словари с допустимыми значениями, получаемые с сайта
        """

        # в этих полях находятся словари сайта с перечнем допустимых значений фильтра
        self._filter_dictionary = self.get_filter_dictionary()
        self._areas_info = self.get_areas_info()
        self._areas_names = self.get_areas_names()

        # параметры фильтра, настроены по умолчанию
        self.parameters = {
            "keyword": None,  # ключевое слово, ищет по всей вакансии
            "page": 0,  # номер страницы
            "count": 100,  # количество вакансий на странице
            "no_agreement": 1,  # не показывать оклад «по договоренности» (когда установлено значение 1)
            "currency": "rub",  # валюта
            "order_field": "date",  # сортировка: по дате публикации/по сумме оклада
            "order_direction": "desc",  # направление сортировки: прямая/обратная

            "town": None,  # ID города
            "experience": None,  # опыт работы
            "type_of_work": None,  # тип занятости
            "payment_from": None,  # сумма оклада от
            "payment_to": None,  # сумма оклада до
            "period": None  # период публикации
        }

    def __str__(self) -> str:
        """Строковое представление экземпляра фильтра"""

        parameters = "\n".join([f"{key}: {value}" for key, value in self.get_filtering_parameters().items()])
        return f"Фильтр для поиска вакансий. Значения:\n" \
               f"{parameters}"

    def __repr__(self) -> str:
        """Строковое представление экземпляра фильтра в режиме отладки"""

        parameters = self.get_all_parameters()
        return f"{self.__class__.__name__}(self._parameters={repr(parameters)})"

    def set_request_parameters(self) -> None:
        """Устанавливает параметры фильтра, использующиеся при отправке запроса на сайт"""

        self.parameters["no_agreement"] = self.ask_no_agreement()

        self.parameters["town"] = self.ask_town()
        self.parameters["experience"] = self.ask_experience()
        self.parameters["type_of_work"] = self.ask_type_of_work()
        self.parameters["payment_from"], self.parameters["payment_to"] = self.ask_payment_from_to()

        self.parameters["period"] = self.ask_period()
        self.parameters["order_field"] = self.ask_order_field()
        self.parameters["order_direction"] = self.ask_order_direction()

    def get_filtering_parameters(self) -> dict:
        """Возвращает параметры фильтра, использующиеся для фильтрации полученных вакансий"""

        f_parameters = ("experience",
                        "type_of_work",
                        "payment_from",
                        "payment_to",
                        "town")

        return {key: value for key, value in self.parameters.items() if key in f_parameters and value is not None}

    def set_filtering_parameters(self) -> None:
        """Устанавливает параметры фильтра, использующиеся для фильтрации полученных вакансий"""

        print("\nУстановка фильтра для SuperJob")

        self.parameters["town"] = self.ask_town()
        self.parameters["experience"] = self.ask_experience()
        self.parameters["type_of_work"] = self.ask_type_of_work()
        self.parameters["payment_from"], self.parameters["payment_to"] = self.ask_payment_from_to()

    def compare_parameters(self, vacancy_dict: dict) -> bool:
        """Проверяет вакансию на соответствие установленным значениям фильтра"""

        vacancy_parameters = {
            "town": vacancy_dict.get("town").get("id") if vacancy_dict.get("town") else None,
            "experience": vacancy_dict.get("experience").get("id") if vacancy_dict.get("experience") else None,
            "type_of_work": vacancy_dict.get("type_of_work").get("id") if vacancy_dict.get("type_of_work") else None,
            "payment_from": vacancy_dict.get("payment_from"),
            "payment_to": vacancy_dict.get("payment_to")
        }

        for key, value in self.get_filtering_parameters().items():
            if key == "salary" and vacancy_parameters[key] < value:
                return False
            elif vacancy_parameters[key] != value:
                return False

        return True

    # блок методов для установки необходимых словарей сайта
    # с предусмотренными значениями фильтра

    def get_filter_dictionary(self) -> dict:
        """
        Возвращает словарь, содержащий надлежащие значения
        для некоторых параметров фильтра
        """

        url = self._FILTER_DICTIONARY
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении словаря дополнительных значений")

    def get_areas_info(self) -> list[dict]:
        """
        Возвращает список словарей, содержащих информацию о городах,
        доступных для поиска вакансий на сайте
        """

        url = self._AREA_CODES
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise requests.RequestException("Ошибка при получении списка кодов")

    def get_areas_names(self) -> list[str]:
        """
        Возвращает список городов и других субъектов,
        доступных для поиска вакансий на сайте
        """

        areas = self._areas_info

        json_exp = jp.parse('$..title')
        matches = json_exp.find(areas)
        codes = [match.value for match in matches]

        return codes

    def get_area_id(self, name: str) -> int:
        """
        Возвращает id переданного функции субъекта,
        если он есть в списке доступных
        """

        regions = self._areas_info

        json_exp = jp.parse("$..towns[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('title') == name]

        if matches:
            return matches[0].get("id")

    # далее идёт блок вопросов к пользователю для установки настроек фильтра !

    @staticmethod
    def ask_keyword() -> str:
        """Запрашивает у пользователя ключевые слова для поиска и возвращает их"""

        return i_input("\nВведите слово или фразу для ключевого запроса:\n")

    @staticmethod
    def ask_no_agreement() -> int:
        """
        Запрашивает у пользователя и возвращает значение 0 или 1 для включения
        или игнорирования вакансий с окладом 'по договоренности'
        """

        text = "Требуется ли исключить вакансии с окладом 'по договоренности'?\n" \
               "Пожалуйста, введите соответствующее числовое значение.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = get_binary_answer(text)

        return 1 if answer == "да" else 0

    @staticmethod
    def ask_order_field() -> str:
        """
        Запрашивает у пользователя и возвращает значение сортировки
        вакансий: по дате или сумме оклада
        """

        text = "Сортировать вакансии по параметру:\n" \
               "Пожалуйста, введите соответствующее числовое значение.\n" \
               "0 - дата\n" \
               "1 - сумма оклада"

        answer = get_binary_answer(text)

        return "date" if answer == "0" else "payment"

    @staticmethod
    def ask_order_direction() -> str:
        """
        Запрашивает у пользователя и возвращает значение направление
        сортировки вакансий: в прямом или обратном порядке
        """

        text = "В каком направлении следует сортировать вакансии?\n" \
               "Пожалуйста, введите соответствующее числовое значение:\n" \
               "0 - в прямом\n" \
               "1 - в обратном"

        answer = get_binary_answer(text)

        return "asc" if answer == "0" else "desc"

    @staticmethod
    def _get_definite_answer(parameter: dict, text: str) -> str:
        """
        Вспомогательная функция для валидации ответа пользователя,
        если значения параметра фильтра ограничены и указаны в словаре сайта
        """

        variations = "\n".join([f"{key} - {value}" for key, value in parameter.items()])

        choice = i_input(f"\nВведите подходящее числовое значение для выбора {text}, "
                         f"либо нажмите Enter для пропуска:\n{variations}\n")

        while choice not in parameter:
            if choice == "":
                break
            choice = i_input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                             f"{variations}\n")

        return choice

    def ask_experience(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'требуемый опыт работы'
        """

        experience = self._filter_dictionary["experience"]
        text = "опыта работы"

        answer = self._get_definite_answer(experience, text)

        return answer if answer else None

    def ask_type_of_work(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'тип занятости'
        """

        type_of_work = self._filter_dictionary["type_of_work"]
        text = "типа занятости"

        answer = self._get_definite_answer(type_of_work, text)

        return answer if answer else None

    def ask_period(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'период публикации' вакансии
        """

        period = self._filter_dictionary["period"]
        text = "периода публикации"

        answer = self._get_definite_answer(period, text)

        return answer if answer else None

    def ask_town(self) -> int | None:
        """
        Запрашивает у пользователя, ищет и возвращает id
        по указанному названию города или другого субъекта,
        если таковой есть в перечне доступных для поиска
        """

        all_towns = sorted(self._areas_names)
        name = i_input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_towns, sep="\n")
                print()
                name = i_input("Попробуйте ещё раз:\n")

            elif name not in all_towns:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = i_input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def _get_right_number(text: str) -> int | None:
        """
        Запрашивает у пользователя и валидирует значение суммы
        на соответствие условиям: сумма должна быть целым положительным числом,
        либо этот параметр будет пропущен (если выражен пустой строкой)
        """

        payment = i_input(f"\nВведите {text} суммы зарплаты для поиска (целое положительное число),\n"
                          f"либо нажмите Enter для пропуска:\n")

        while payment != "":
            if payment.isdigit():
                payment = int(payment)
                break
            payment = i_input("Сумма должна быть целым положительным числом без каких-либо знаков.\n"
                              "Попробуйте еще раз:\n")

        return payment if payment else None

    def ask_payment_from_to(self) -> tuple | list:
        """
        Запрашивает у пользователя и возвращает нижнюю
        и верхнюю границы зарплаты для поиска
        """

        text = "нижнюю границу"
        payment_from = self._get_right_number(text)

        text = "верхнюю границу"
        payment_to = self._get_right_number(text)

        try:
            return sorted((payment_from, payment_to))
        except TypeError:
            return payment_from, payment_to
