"""Чтение стартового скрипта."""


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def read_script(path):
    """Читает скрипт и возвращает список пар (номер строки, строка).

    Пустые строки пропускаются, номера остаются исходными. Комментарии
    (символ #) обрабатывает парсер команд. Бросает ScriptError, если
    файл нельзя прочитать.
    """
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except OSError as error:
        reason = error.strerror or str(error)
        raise ScriptError(f"cannot read '{path}': {reason}") from error
    except UnicodeDecodeError as error:
        raise ScriptError(f"'{path}' is not a UTF-8 text file") from error
    numbered = enumerate(lines, start=1)
    return [(number, line) for number, line in numbered if line.strip()]
