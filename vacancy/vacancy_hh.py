import requests

from sources.constants import CBR_RATE_URL
from vacancy.vacancy_abc import Vacancy


class VacancyHeadHunter(Vacancy):
    """Класс для описания вакансии, полученной с сайта HeadHunter"""

    def __init__(self, vacancy_dict: dict) -> None:
        """
        Инициализатор объектов класса, устанавливает некоторые
        избранные значения из словаря вакансии
        Отдельно сохраняет полную информацию о вакансии (весь словарь)

        :param vacancy_dict: словарь с информацией о вакансии
        """

        self.name = vacancy_dict.get("name")
        self.area = vacancy_dict.get("area")
        self.alternate_url = vacancy_dict.get("alternate_url")
        self.requirement = vacancy_dict.get("snippet")
        self.responsibility = vacancy_dict.get("snippet")
        self.professional_roles = vacancy_dict.get("professional_roles")
        self.experience = vacancy_dict.get("experience")
        self.employment = vacancy_dict.get("employment")

        salary = vacancy_dict.get("salary")
        self.salary_from = salary.get("from") if salary else None
        self.salary_to = salary.get("to") if salary else None
        self.currency = salary.get("currency") if salary else None

        self.salary_from_rub = self.salary_from
        self.salary_to_rub = self.salary_to

        self.full_info = vacancy_dict

    def __str__(self) -> str:
        """Строковое представление вакансии"""

        return f"'name': {self.name}\n" \
               f"'url': {self.alternate_url}"

    def __repr__(self) -> str:
        """Строковое представление вакансии для режима отладки"""

        full_info = "\n".join({f"{key}: {value}" for key, value in self.full_info.items()})
        return f"{self.__class__.__name__}(\n" \
               f"{full_info}\n" \
               f")"

    def __setattr__(self, key, value) -> None:
        """
        При установке свойств объектов класса убирает текстовые артефакты
        из полей требования и обязанности;
        Устанавливает правила конвертации суммы зарплаты в рубли
        """

        if key in ("requirement", "responsibility"):
            value = value.get(key) if value else None
            artefacts = ("<highlighttext>", "</highlighttext>")
            for string in artefacts:
                if value and string in value:
                    value = value.replace(string, "")

        elif key in ("salary_from_rub", "salary_to_rub") and self.currency != "RUR":
            value = self.convert_currency(value, self.currency)

        super().__setattr__(key, value)

    @staticmethod
    def convert_currency(number: int | None, currency: str | None) -> int:
        """
        Конвертирует сумму в иностранной валюте в эквивалентную сумму в рублях,
        основываясь на данных ЦБР, получаемых с сайта
        """

        response = requests.get(CBR_RATE_URL)
        if response.status_code != 200:
            raise requests.RequestException("Ошибка при загрузке словаря с текущим курсом валют")
        currency_dictionary = response.json().get("Valute")

        number_rub = 0

        if currency in currency_dictionary and number:
            number_rub = currency_dictionary[currency]["Value"] * number

        return number_rub

    def get_min_salary(self) -> int:
        """
        Находит минимальное из присущих вакансии значений заработной платы,
        при отсутствии и верхней, и нижней границ зарплаты, возвращает 0
        """

        salary_range = (self.salary_from_rub, self.salary_to_rub)
        min_salary = 0

        if any(salary_range):
            min_salary = min([salary for salary in salary_range if salary])

        return min_salary

    def get_short_info(self) -> dict:
        """Возвращает краткую информацию о вакансии"""

        name = self.name
        area = self.area.get('name', "Не указано") if self.area else "Не указано"
        salary_from = self.salary_from
        salary_to = self.salary_to
        currency = self.currency if self.currency else ""
        alternate_url = self.alternate_url
        requirement = self.requirement if self.requirement else "Не указано"
        responsibility = self.responsibility if self.responsibility else "Не указано"

        experience = self.experience.get('name', "Не указано") if self.experience else "Не указано"
        employment = self.employment.get('name', "Не указано") if self.employment else "Не указано"

        str_salary = "Не указано"
        if all((salary_from, salary_to)):
            str_salary = f"{salary_from} - {salary_to} {currency}"
        elif any((salary_from, salary_to)):
            str_salary = f"{salary_from or salary_to} {currency}"

        str_professional_roles = "Не указано"
        if self.professional_roles:
            professional_roles = [role.get("name", "Не указано") for role in self.professional_roles]
            str_professional_roles = ", ".join(professional_roles)

        return {"Название": name,
                "Город": area,
                "Зарплата": str_salary,
                "Ссылка": alternate_url,
                "Требования": requirement,
                "Обязанности": responsibility,
                "Профессиональные роли": str_professional_roles,
                "Опыт": experience,
                "Занятость": employment}
