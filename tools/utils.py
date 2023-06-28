def i_input(*args, **kwargs) -> str:
    """
    Функция для замещения стандартного input,
    позволяет прервать программу на любом этапе ввода,
    если введенное пользователем слово это 'stop'
    """

    result = input(*args, **kwargs)
    if result == "stop":
        print("\nСпасибо и всего доброго!")
        quit()
    return result


def get_binary_answer(text: str) -> str:
    """
    Вспомогательная функция для получения и валидации бинарных ответов
    (да/нет, 0/1, то/это)

    :param text: строка с вопросом, описывающая ситуацию и варианты ответа
    :return: выбранный вариант ответа '0' или '1'
    """

    answer = i_input(f"\n{text}\n")

    while answer not in ("0", "1"):
        answer = i_input("Пожалуйста, введите ответ в формате числа в заданном диапазоне значений.\n")

    return answer
