"""Команды эмулятора."""


class ExitRequested(Exception):
    """Сигнал о том, что пользователь запросил выход."""


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
    """
    if not tokens:
        return ""
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        return f"{name}: command not found"
    return handler(args)
