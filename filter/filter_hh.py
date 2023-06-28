import requests
import jsonpath_ng as jp

from sources.headhunter import urls_hh
from tools.utils import i_input, get_binary_answer
from filter.filter_abc import Filter


class FilterHH(Filter):
    """
    Класс для настройки фильтра запроса на сайт HeadHunter
    и последующей фильтрации полученных вакансий
    """

    # ссылка на ресурс, возвращающий весь перечень регионов/городов
    _AREA_CODES = urls_hh.AREA_CODES
    # ссылка на ресурс, возвращающий словари со значениями для фильтра
    _FILTER_DICTIONARY = urls_hh.FILTER_DICTIONARY

    # словарь с возможными доменами для поиска
    _HOSTS = {"0": "hh.ru",
              "1": "rabota.by",
              "2": "hh1.az",
              "3": "hh.uz",
              "4": "hh.kz",
              "5": "headhunter.ge",
              "6": "headhunter.kg"
              }

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
            "text": None,  # ключевое слово, ищет по всей вакансии
            "page": 0,  # номер страницы
            "per_page": 100,  # количество вакансий на странице
            "host": "hh.ru",  # доменное имя сайта
            "only_with_salary": False,  # показывать вакансии только с указанием зарплаты, по умолчанию False
            "locale": "RU",  # идентификатор локали
            "period": None,  # количество дней, в пределах которых производится поиск по вакансиям
            "order_by": None,  # сортировка списка вакансий

            "experience": None,  # опыт работы
            "employment": None,  # тип занятости
            "salary": None,  # размер заработной платы
            "currency": None,  # код валюты, имеет смысл указывать только вместе с salary
            "area": None  # регион, город

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

        self.parameters["host"] = self.ask_host()
        self.parameters["only_with_salary"] = self.ask_only_with_salary()
        self.parameters["locale"] = self.ask_locale()

        self.parameters["area"] = self.ask_area()
        self.parameters["experience"] = self.ask_experience()
        self.parameters["employment"] = self.ask_employment()

        self.parameters["salary"] = self.ask_salary()
        if self.parameters.get("salary"):
            self.parameters["currency"] = self.ask_currency()

        self.parameters["period"] = self.ask_period()
        self.parameters["order_by"] = self.ask_order_by()

    def get_filtering_parameters(self) -> dict:
        """Возвращает параметры фильтра, использующиеся для фильтрации полученных вакансий"""

        f_parameters = ("experience",
                        "employment",
                        "salary",
                        "currency",
                        "area")

        return {key: value for key, value in self.parameters.items() if key in f_parameters and value is not None}

    def set_filtering_parameters(self) -> None:
        """Устанавливает параметры фильтра, использующиеся для фильтрации полученных вакансий"""

        print("\nУстановка фильтра для HeadHunter")

        self.parameters["area"] = self.ask_area()
        self.parameters["experience"] = self.ask_experience()
        self.parameters["employment"] = self.ask_employment()

        self.parameters["salary"] = self.ask_salary()
        if self.parameters.get("salary"):
            self.parameters["currency"] = self.ask_currency()

    def compare_parameters(self, vacancy_dict: dict) -> bool:
        """Проверяет вакансию на соответствие установленным значениям фильтра"""

        salary = vacancy_dict.get("salary")
        min_salary = 0

        if salary:
            salary_range = salary.get("from", 0), salary.get("to", 0)

            if any(salary_range):
                min_salary = min([salary for salary in salary_range if type(salary) is int])

        vacancy_parameters = {
            "area": vacancy_dict.get("area").get("id") if vacancy_dict.get("area") else None,
            "experience": vacancy_dict.get("experience").get("id") if vacancy_dict.get("experience") else None,
            "employment": vacancy_dict.get("employment").get("id") if vacancy_dict.get("employment") else None,
            "salary": min_salary,
            "currency": salary.get("currency") if salary else None
        }

        for key, value in self.get_filtering_parameters().items():
            if key == "salary" and vacancy_parameters[key] < value:
                return False
            elif key != "salary" and vacancy_parameters[key] != value:
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

        json_exp = jp.parse('$..name')
        matches = json_exp.find(areas)
        names = [match.value for match in matches]

        return names

    def get_area_id(self, name: str) -> str:
        """
        Возвращает id переданного функции субъекта,
        если он есть в списке доступных
        """

        regions = self._areas_info

        json_exp = jp.parse("$..areas[*]")
        matches = [match.value for match in json_exp.find(regions) if match.value.get('name') == name]

        if matches:
            return matches[0].get("id")

    # далее идёт блок вопросов к пользователю для установки настроек фильтра !

    @staticmethod
    def ask_text() -> str:
        """Запрашивает у пользователя ключевое слово для поиска и возвращает его"""

        return i_input("\nВведите слово или фразу для ключевого запроса:\n")

    def ask_host(self) -> str:
        """
        Запрашивает у пользователя и возвращает выбранное
        доменное имя сайта для запроса
        """

        hosts = "\n".join([f"{num} - {host}" for num, host in self._HOSTS.items()])

        choice = i_input(f"\nКакое доменное имя сайта использовать для запроса? "
                         f"По умолчанию используется 'hh.ru'.\n"
                         f"Доступны варианты:\n{hosts}\n"
                         f"Введите номер выбранного домена или '0' чтобы оставить значение по умолчанию.\n")

        while choice not in self._HOSTS:
            choice = i_input("Неверный номер. Пожалуйста, повторите попытку:\n")

        return self._HOSTS[choice]

    @staticmethod
    def ask_only_with_salary() -> bool:
        """
        Запрашивает у пользователя возвращает значение, в зависимости от которого
        запрос будет включать или игнорировать вакансии без указания заработной платы
        """

        text = "Выводить только вакансии с указанием заработной платы? " \
               "Пожалуйста, введите ответ в формате числа.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = get_binary_answer(text)

        return True if answer == "1" else False

    @staticmethod
    def ask_locale() -> str:
        """
        Запрашивает у пользователя возвращает значение локализации
        в зависимости от выбора пользователя
        """

        text = "Требуется ли изменить язык локализации на английский?\n" \
               "По умолчанию стоит русская локализация. " \
               "Пожалуйста, введите ответ в формате числа.\n" \
               "0 - нет\n" \
               "1 - да"

        answer = get_binary_answer(text)

        return "EN" if answer == "1" else "RU"

    @staticmethod
    def _get_definite_answer(parameter: list, text: str) -> str:
        """
        Вспомогательная функция для валидации ответа пользователя,
        если значения параметра фильтра ограничены и указаны в словаре сайта
        """

        variations = "\n".join([f"{i} - {field['name']}" for i, field in enumerate(parameter)])
        choice = i_input(f"\n{text}\n{variations}\n"
                         f"Введите номер, либо нажмите Enter для пропуска.\n")

        while choice != "":
            if choice.isdigit() and 0 <= int(choice) < len(parameter):
                return choice

            choice = i_input(f"Введите существующий номер, либо нажмите Enter для пропуска.\n"
                             f"{variations}\n")

        return choice

    def ask_experience(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'требуемый опыт работы'
        """

        experience = self._filter_dictionary["experience"]
        text = "Выберите требуемый опыт работы:"
        answer = self._get_definite_answer(experience, text)

        return experience[int(answer)]["id"] if answer.isdigit() else None

    def ask_employment(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'вид занятости'
        """

        employment = self._filter_dictionary["employment"]
        text = "Выберите требуемый вид занятости:"
        answer = self._get_definite_answer(employment, text)

        return employment[int(answer)]["id"] if answer.isdigit() else None

    def ask_currency(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'валюта зарплаты'
        """

        currency = [field for field in self._filter_dictionary["currency"] if field["in_use"]]
        text = "Выберите валюту зарплаты:"
        answer = self._get_definite_answer(currency, text)

        return currency[int(answer)]["code"] if answer.isdigit() else None

    def ask_order_by(self) -> str | None:
        """
        Запрашивает у пользователя и возвращает значение
        параметра 'способ сортировки'
        """

        order_by = [field for field in self._filter_dictionary["vacancy_search_order"] if field["id"] != "distance"]
        text = "Выберите способ сортировки:"
        answer = self._get_definite_answer(order_by, text)

        return order_by[int(answer)]["id"] if answer.isdigit() else None

    def ask_area(self) -> str | None:
        """
        Запрашивает у пользователя, ищет и возвращает id
        по указанному названию города или другого субъекта,
        если таковой есть в перечне доступных для поиска
        """

        all_areas = sorted(self._areas_names)
        name = i_input("\nВведите город или населенный пункт, либо нажмите Enter для пропуска:\n")

        while name != "":

            if name == "list":
                print()
                print(*all_areas, sep="\n")
                print()
                name = i_input("Попробуйте ещё раз:\n")

            elif name not in all_areas:
                print(f"Не могу найти такой населенный пункт.\n"
                      f"Для вызова списка городов введите 'list'.\n"
                      f"Соблюдайте регистр.")
                name = i_input("Попробуйте ещё раз:\n")

            else:
                break

        return self.get_area_id(name)

    @staticmethod
    def _get_right_number(text: str) -> int | str:
        """
        Запрашивает и проверяет ответ пользователя,
        который должен быть либо целым положительным числом,
        либо пустой строкой
        """

        answer = i_input(f"\nВведите {text} (целое положительное число),\n"
                         f"либо нажмите Enter для пропуска:\n")

        while answer != "":
            if answer.isdigit():
                answer = int(answer)
                break
            answer = i_input("Введите целое положительное число без каких-либо знаков.\n"
                             "Попробуйте еще раз:\n")

        return answer

    def ask_salary(self) -> int | None:
        """
        Запрашивает и возвращает значение суммы зарплаты для поиска,
        если оно представлено целым положительным числом
        """

        text = "сумму зарплаты для поиска"
        salary = self._get_right_number(text)

        return salary if salary else None

    def ask_period(self) -> int | None:
        """
        Запрашивает и возвращает количество дней, в пределах которых
        производится поиск, если оно представлено целым положительным числом
        """

        text = "количество дней, в пределах которых производится поиск по вакансиям"
        period = self._get_right_number(text)

        return period if period else None
