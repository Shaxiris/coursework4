from abc import ABC, abstractmethod


class Vacancy(ABC):
    """Абстрактный класс для описания вакансии"""

    # обязательный атрибут, словарь с полной информацией о вакансии
    full_info = {}

    def get_parameters(self) -> dict:
        """Возвращает все установленные свойства вакансии"""

        return self.__dict__

    def __eq__(self, other):
        """Описывает условия равенства объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() == other.get_min_salary()

    def __ne__(self, other):
        """Описывает условия неравенства объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() != other.get_min_salary()

    def __lt__(self, other):
        """Описывает условия сравнения по знаку '<' объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() < other.get_min_salary()

    def __le__(self, other):
        """Описывает условия сравнения по знаку '<=' объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() <= other.get_min_salary()

    def __gt__(self, other):
        """Описывает условия сравнения по знаку '>' объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() > other.get_min_salary()

    def __ge__(self, other):
        """Описывает условия сравнения по знаку '>=' объектов вакансии"""

        if isinstance(other, Vacancy):
            return self.get_min_salary() >= other.get_min_salary()

    @abstractmethod
    def get_min_salary(self) -> int:
        """Находит минимальное из присущих вакансии значений заработной платы"""
        pass

    @abstractmethod
    def get_short_info(self) -> dict:
        """Возвращает краткую информацию о вакансии"""
        pass
