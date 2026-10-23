"""Реестр команд эмулятора."""

from src.cmd_fs import cmd_cd, cmd_du, cmd_ls
from src.cmd_text import cmd_uniq
from src.errors import CommandError, ExitRequested, VFSError


def cmd_exit(vfs, args):
    """exit: завершить работу эмулятора."""
    raise ExitRequested


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "du": cmd_du,
    "uniq": cmd_uniq,
    "exit": cmd_exit,
}


def execute(vfs, tokens):
    """Выполняет команду над VFS и возвращает текст для вывода.

    Первый токен — имя команды, остальные — аргументы. Бросает
    CommandError, если команда неизвестна или завершилась ошибкой;
    к сообщению добавляется имя команды.
    """
    if not tokens:
        return ""
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"{name}: command not found")
    try:
        return handler(vfs, args)
    except (CommandError, VFSError) as error:
        raise CommandError(f"{name}: {error}") from error
