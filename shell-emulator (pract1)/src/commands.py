"""Команды эмулятора."""

from src.errors import CommandError, ExitRequested


def cmd_ls(args):
    """Заглушка ls: выводит своё имя и аргументы."""
    return f"ls: args={args}"


def cmd_cd(args):
    """Заглушка cd: выводит своё имя и аргументы."""
    return f"cd: args={args}"


def cmd_exit(args):
    """Завершает работу эмулятора."""
    raise ExitRequested


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(tokens):
    """Выполняет команду и возвращает текст для вывода.

    Первый токен — имя команды, остальные — аргументы.
    Бросает CommandError, если команда неизвестна.
    """
    if not tokens:
        return ""
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"{name}: command not found")
    return handler(args)
