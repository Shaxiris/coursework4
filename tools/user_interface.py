import os

from request_api.request_api_hh import HeadHunterAPI
from request_api.request_api_sj import SuperJobAPI
from saver.json_saver import JSONSaver
from tools.utils import i_input, get_binary_answer
from sources.constants import PATH_FILE_FULL_INFO_VACANCIES, PATH_FILE_SHORT_INFO_VACANCIES, PATH_DIR_JSON
from sources.constants import MAX_LENGTH_NAME
from vacancy.vacancy_hh import VacancyHeadHunter
from vacancy.vacancy_sj import VacancySuperJob
from vacancy.vacancy_abc import Vacancy
from filter.filter_hh import FilterHH
from filter.filter_sj import FilterSJ
from filter.filter_abc import Filter


def user_interaction() -> None:
    """Основная, главная функция для взаимодействия с пользователем"""

    print("Добрый день! Я помогу вам найти вакансии.")
    print()
    print("В любой момент ввода текста с клавиатуры вы можете завершить программу.\n"
          "Для этого наберите слово 'stop' в точности как указано.")

    vacancies = find_vacancies()

    is_exit = None

    while is_exit != "1":

        text = "В каком виде вывести информацию?\n" \
               "0 - Вывести все вакансии\n" \
               "1 - Настроить фильтр для вывода вакансий"
        is_set_filter = get_binary_answer(text)

        list_vacancies = None

        if is_set_filter == "0":
            list_vacancies = create_all_vacancies(vacancies)

        elif is_set_filter == "1":
            list_vacancies = create_definite_vacancies(vacancies)

        results = sort_vacancies(list_vacancies)

        show_vacancies(results)

        select_recording_method(results)

        text = "Выберите следующий шаг:\n" \
               "0 - Настроить другие фильтры и записать информацию\n" \
               "1 - Завершить работу программы"

        is_exit = get_binary_answer(text)

    print("\nСпасибо и всего доброго!")


def find_vacancies() -> list[dict]:
    """
    Функция для поиска вакансий по запросу.
    Пока пользователь не прервет работу функции,
    будет запрашивать настройку фильтров
    и собирать информацию о вакансиях с сайта, расширяя список
    """

    results = []

    while True:

        request_filter = None
        request_api = None

        website = choice_website()

        if website == "0":
            request_filter = FilterHH()
            request_filter.parameters["text"] = request_filter.ask_text()
            request_api = HeadHunterAPI

        elif website == "1":
            request_filter = FilterSJ()
            request_filter.parameters["keyword"] = request_filter.ask_keyword()
            request_api = SuperJobAPI

        request = request_api(*set_request_filter(request_filter))

        vacancies = request.get_vacancies()

        for vacancy in vacancies:
            if vacancy not in results:
                results.append(vacancy)

        operations = {
            0: "Добавить больше вакансий в список",
            1: "Очистить список и найти новые вакансии",
            2: "Показать результаты поиска"
        }

        operation = choice_operation(operations)

        if operation == 0:
            continue
        elif operation == 1:
            results.clear()
            continue
        elif operation == 2:
            break

    return results


def choice_website() -> str:
    """Вспомогательная функция для выбора вебсайта из предложенного списка"""

    websites = get_websites()

    websites_print = "\n".join([f"{i}: {site}" for i, site in enumerate(websites)])
    answer = i_input(f"\nНа каком сайте искать вакансии? "
                     f"Пожалуйста, введите номер, соответствующий ресурсу.\n"
                     f"{websites_print}\n")

    while check_int(answer) not in range(len(websites)):
        answer = i_input("\nПожалуйста, введите номер, соответствующий ресурсу.\n")

    return answer


def get_websites() -> list[str]:
    """Вспомогательная функция для возвращения списка доступных сайтов,
    эту информацию получает из файла 'urls.txt' """

    root_dir = os.path.dirname(os.path.dirname(__file__))
    path_websites = os.path.join(root_dir, "sources", "urls.txt")
    with open(path_websites, "r", encoding="utf-8") as file:
        websites = file.read().split("\n")

    return websites


def check_int(number: str) -> int:
    """
    Вспомогательная функция.
    Пока пользователь не введёт информацию в виде целого положительного числа,
    будет запрашивать ввод
    """

    while True:
        try:
            return int(number)
        except ValueError:
            number = i_input("\nОтвет должен быть выражен целым числом.\n")
            continue


def set_request_filter(request_filter: Filter) -> tuple:
    """Уточняет у пользователя настройку фильтра запроса,
    а также желаемое количество вакансий для поиска"""

    text = "Настроить фильтр или использовать параметры по умолчанию?\n" \
           "0 - использовать параметры по умолчанию\n" \
           "1 - настроить фильтр самостоятельно"

    answer = get_binary_answer(text)

    if answer == "1":
        request_filter.set_request_parameters()

    number = get_number()

    return request_filter, number


def get_number() -> int:
    """Получает от пользователя желаемое число вакансий в заданном диапазоне"""

    answer = i_input("\nПожалуйста, введите желаемое количество вакансий. "
                     "Число должно быть больше 0 и не больше 500.\n"
                     "В противном случае будет установлено значение по умолчанию = 10)\n")

    return check_int(answer)


def choice_operation(operations: dict) -> int:
    """Запрашивает у пользователя выбор конкретной операции из словаря доступных операций"""

    operations_print = "\n".join([f"{key}: {value}" for key, value in operations.items()])

    operation = None

    while operation not in operations:
        operation = i_input(f"\nПожалуйста, выберите номер следующей операции.\n"
                            f"{operations_print}\n")
        operation = check_int(operation)

    return operation


def create_all_vacancies(vacancies: list[dict]) -> list[Vacancy]:
    """Создает и возвращает объекты вакансий, если не заданы значений фильтра"""

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


def create_definite_vacancies(vacancies: list[dict]) -> list[Vacancy]:
    """
    Устанавливает значения фильтра,
    создаёт и возвращает список объектов вакансий,
    в соответствии с заданными фильтрами
    """

    list_vacancies = []

    websites = get_websites()

    operations = {
        0: f"Настроить фильтр и вывести вакансии с сайта {websites[0]}",
        1: f"Настроить фильтр и вывести вакансии с сайта {websites[1]}",
        2: "Настроить оба фильтра и вывести вакансии с обоих сайтов"
    }

    operation = choice_operation(operations)

    filter_obj_hh = None
    filter_obj_sj = None

    if operation == 0:
        filter_obj_hh = FilterHH()
        filter_obj_hh.set_filtering_parameters()

    elif operation == 1:
        filter_obj_sj = FilterSJ()
        filter_obj_sj.set_filtering_parameters()

    elif operation == 2:
        filter_obj_hh, filter_obj_sj = (FilterHH(), FilterSJ())
        filter_obj_hh.set_filtering_parameters()
        filter_obj_sj.set_filtering_parameters()

    for vacancy in vacancies:
        if "hh.ru" in vacancy.get("url", ""):
            if filter_obj_hh and filter_obj_hh.compare_parameters(vacancy):
                vacancy = VacancyHeadHunter(vacancy)
                list_vacancies.append(vacancy)
        elif "superjob.ru" in vacancy.get("link", ""):
            if filter_obj_sj and filter_obj_sj.compare_parameters(vacancy):
                vacancy = VacancySuperJob(vacancy)
                list_vacancies.append(vacancy)

    return list_vacancies


def sort_vacancies(list_objects: list[Vacancy]) -> list[Vacancy]:
    """
    Сортирует список вакансий по заданному порядку
    в указанном пользователем количестве
    """

    max_quantity = len(list_objects)

    text = "Отсортировать вакансии по зарплате?\n" \
           "0 - Нет\n" \
           "1 - Да"

    sorting = int(get_binary_answer(text))

    if sorting:

        text = "В каком порядке выполнить сортировку?\n" \
               "0 - В порядке возрастания\n" \
               "1 - В порядке убывания"

        reverse = True if int(get_binary_answer(text)) else False

        list_objects = sorted(list_objects, reverse=reverse)

    quantity = i_input(f"\nСколько вакансий вывести? "
                       f"Возможный максимум - {max_quantity}\n"
                       f"Чтобы вывести все, нажмите Enter\n")

    while quantity != "":
        if quantity.isdigit() and int(quantity) <= max_quantity:
            break
        quantity = i_input("Значение должно быть целым положительным числом меньше максимума.\n")

    if quantity:
        return list_objects[:int(quantity)]

    return list_objects


def show_vacancies(list_objects: list[Vacancy]) -> None:
    """Выводит вакансии на экран в читаемом виде"""

    short_info = [object.get_short_info() for object in list_objects]

    for info in short_info:
        print()
        print("\n".join([f"{key}: {value}" for key, value in info.items()]))


def select_recording_method(list_objects: list[Vacancy]) -> None:
    """Функция выбора действий для записи информации о найденных вакансий в файл"""

    operations = {
        0: "Добавить отсортированные вакансии в существующий файл 'vacancies'",
        1: "Перезаписать информацию в файл 'vacancies', удалив из него предыдущие записи",
        2: "Полностью очистить файл 'vacancies' и ничего не записывать",
        3: "Записать отсортированные вакансии в новый файл",
        4: "Не записывать информацию"
    }

    operation = choice_operation(operations)

    if operation == 0:
        add_vacancies_to_file(list_objects)

    elif operation == 1:
        write_vacancies_to_file(list_objects)

    elif operation == 2:
        clean_vacancies_file()

    elif operation == 3:
        create_new_vacancies_file(list_objects)

    elif operation == 4:
        print("\nИнформация не была записана в файл")


def add_vacancies_to_file(list_objects: list[Vacancy]) -> None:
    """
    Функция для добавления информации о найденных вакансиях
    в непустой файл по умолчанию
    """

    json_saver_full = JSONSaver(PATH_FILE_FULL_INFO_VACANCIES)
    json_saver_short = JSONSaver(PATH_FILE_SHORT_INFO_VACANCIES)
    full_info = [object.full_info for object in list_objects]
    short_info = [object.get_short_info() for object in list_objects]
    print(type(short_info))

    json_saver_full.add_vacancies(full_info)
    json_saver_short.add_vacancies(short_info)


def write_vacancies_to_file(list_objects: list[Vacancy]) -> None:
    """
    Функция для записи информации о найденных вакансиях
    в пустой файл по умолчанию
    """

    json_saver_full = JSONSaver(PATH_FILE_FULL_INFO_VACANCIES)
    json_saver_short = JSONSaver(PATH_FILE_SHORT_INFO_VACANCIES)
    full_info = [object.full_info for object in list_objects]
    short_info = [object.get_short_info() for object in list_objects]

    json_saver_full.write_vacancies(full_info)
    json_saver_short.write_vacancies(short_info)


def clean_vacancies_file() -> None:
    """Удаляет всю информацию о вакансиях из файла по умолчанию"""

    json_saver_full = JSONSaver(PATH_FILE_FULL_INFO_VACANCIES)
    json_saver_short = JSONSaver(PATH_FILE_SHORT_INFO_VACANCIES)

    json_saver_full.clean_file()
    json_saver_short.clean_file()


def create_new_vacancies_file(list_objects: list[Vacancy]) -> None:
    """
    Создает новый файл, имя которому задаёт пользователь
    и записывает в него информацию о вакансиях.
    Добавление информации в этот файл программно не предусмотрено
    """

    new_file = input("\nПожалуйста, введите название файла.\n"
                     "Допустимы только буквы, цифры и знак '_'\n"
                     f"Максимальная длина имени файла - {MAX_LENGTH_NAME}\n")

    while not check_file_name(new_file):
        new_file = input("\nПожалуйста, введите название файла.\n"
                         "Допустимы только буквы, цифры и знак '_'\n"
                         f"Максимальная длина имени файла - {MAX_LENGTH_NAME}\n")

    file_name_full = new_file + "(full_info).json"
    path_new_file_full = (*PATH_DIR_JSON, file_name_full)
    file_name_short = new_file + "(short_info).json"
    path_new_file_short = (*PATH_DIR_JSON, file_name_short)

    json_saver_full = JSONSaver(path_new_file_full)
    json_saver_short = JSONSaver(path_new_file_short)
    full_info = [object.full_info for object in list_objects]
    short_info = [object.get_short_info() for object in list_objects]

    json_saver_full.write_vacancies(full_info)
    json_saver_short.write_vacancies(short_info)


def check_file_name(name: str) -> bool:
    """
    Проверяет введенное пользователем имя для файла
    на соответствие условиям:
    имя может состоять только из букв, цифр, знака '_'
    Максимальная длина имени файла не больше 20 символов
    """

    if len(name) > MAX_LENGTH_NAME:
        return False

    for sign in name:
        if not sign.isalnum() and sign != "_":
            return False

    return True
