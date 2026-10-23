"""Разбор введённой пользователем строки."""

import os
import shlex


class ParseError(Exception):
    """Ошибка разбора командной строки."""


def parse_line(line):
    """Раскрывает переменные окружения и делит строку на токены.

    Всё после символа # (вне кавычек) считается комментарием.
    Возвращает список токенов, для пустой строки список пустой.
    Бросает ParseError, если разобрать строку нельзя.
    """
    expanded = os.path.expandvars(line)
    try:
        return shlex.split(expanded, comments=True)
    except ValueError as error:
        raise ParseError(str(error)) from error
