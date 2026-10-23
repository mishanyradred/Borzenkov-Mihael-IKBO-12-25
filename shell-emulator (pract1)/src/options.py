"""Разбор флагов команд."""

from src.errors import CommandError

END_OF_OPTIONS = "--"


def check_flags(letters, allowed):
    """Проверяет буквы флагов и возвращает их множество."""
    for letter in letters:
        if letter not in allowed:
            raise CommandError(f"invalid option -- '{letter}'")
    return set(letters)


def split_options(args, allowed):
    """Делит аргументы на множество флагов и список операндов.

    Флаги состоят из одной буквы и могут объединяться (-la). Строка «--»
    заканчивает флаги, одиночный «-» считается операндом. Бросает
    CommandError, если встретился флаг не из строки allowed.
    """
    flags = set()
    operands = []
    options_done = False
    for arg in args:
        if options_done or arg == "-" or not arg.startswith("-"):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            flags.update(check_flags(arg[1:], allowed))
    return flags, operands
