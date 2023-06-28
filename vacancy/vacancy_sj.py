from vacancy.vacancy_abc import Vacancy


class VacancySuperJob(Vacancy):
    """Класс для описания вакансии, полученной с сайта SuperJob"""

    def __init__(self, vacancy_dict: dict) -> None:
        """
        Инициализатор объектов класса, устанавливает некоторые
        избранные значения из словаря вакансии
        Отдельно сохраняет полную информацию о вакансии (весь словарь)

        :param vacancy_dict: словарь с информацией о вакансии
        """

        self.profession = vacancy_dict.get("profession")
        self.town = vacancy_dict.get("town")
        self.payment_from = vacancy_dict.get("payment_from")
        self.payment_to = vacancy_dict.get("payment_to")
        self.currency = vacancy_dict.get("currency")
        self.link = vacancy_dict.get("link")
        self.description = vacancy_dict.get("candidat")
        self.experience = vacancy_dict.get("experience")
        self.type_of_work = vacancy_dict.get("type_of_work")

        self.full_info = vacancy_dict

    def __str__(self) -> str:
        """Строковое представление вакансии"""

        return f"'profession': {self.profession}\n" \
               f"'url': {self.link}"

    def __repr__(self) -> str:
        """Строковое представление вакансии для режима отладки"""

        full_info = "\n".join({f"{key}: {value}" for key, value in self.full_info.items()})
        return f"{self.__class__.__name__}(\n" \
               f"{full_info}\n" \
               f")"

    def __setattr__(self, key, value) -> None:
        """
        При установке свойств объектов класса расставляет отступы
        в значении поля description для более читаемого вывода
        """

        if key == "description":
            value = "\n\t" + value.replace("\n\n", "\n").replace("\n", "\n\t")
        super().__setattr__(key, value)

    def get_min_salary(self) -> int:
        """
        Находит минимальное из присущих вакансии значений заработной платы,
        при отсутствии и верхней, и нижней границ зарплаты, возвращает 0
        """

        salary_range = (self.payment_from, self.payment_to)
        min_salary = 0

        if all(salary_range):
            min_salary = min([salary for salary in salary_range if type(salary) is int])
        elif any(salary_range):
            min_salary = salary_range[0] or salary_range[1]

        return min_salary

    def get_short_info(self) -> dict:
        """Возвращает краткую информацию о вакансии"""

        profession = self.profession
        town = self.town.get("title", "Не указано") if self.town else "Не указано"
        payment_from = self.payment_from
        payment_to = self.payment_to
        currency = self.currency if self.currency else ""
        link = self.link
        description = self.description if self.description else "Не указано"

        experience = self.experience.get("title", "Не указано") if self.experience else "Не указано"
        type_of_work = self.type_of_work.get("title", "Не указано") if self.type_of_work else "Не указано"

        str_salary = "Не указано"
        if all((payment_from, payment_to)):
            str_salary = f"{payment_from} - {payment_to} {currency}"
        elif any((payment_from, payment_to)):
            str_salary = f"{payment_from or payment_to} {currency}"

        return {"Название": profession,
                "Город": town,
                "Зарплата": str_salary,
                "Ссылка": link,
                "Описание": description,
                "Опыт": experience,
                "Занятость": type_of_work}
