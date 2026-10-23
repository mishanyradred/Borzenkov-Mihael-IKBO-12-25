"""Команды обработки текста: uniq."""

from src.errors import CommandError
from src.options import split_options

SINGLE = 1


def read_lines(vfs, path):
    """Читает текстовый файл из VFS и возвращает список его строк."""
    node = vfs.get(path)
    if node.is_dir:
        raise CommandError(f"{path}: Is a directory")
    try:
        return node.data.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise CommandError(f"{path}: not a text file") from error


def group_lines(lines, ignore_case):
    """Склеивает соседние одинаковые строки в пары [строка, счётчик]."""
    groups = []
    previous = None
    for line in lines:
        key = line.lower() if ignore_case else line
        if groups and key == previous:
            groups[-1][1] += 1
        else:
            groups.append([line, SINGLE])
        previous = key
    return groups


def select_groups(groups, flags):
    """Оставляет группы согласно флагам -d (повторы) и -u (уникальные)."""
    if "d" in flags:
        groups = [group for group in groups if group[1] != SINGLE]
    if "u" in flags:
        groups = [group for group in groups if group[1] == SINGLE]
    return groups


def cmd_uniq(vfs, args):
    """uniq [-c] [-d] [-u] [-i] файл: убрать соседние повторы строк.

    -c — перед строкой выводить число повторов, -d — только повторяющиеся
    строки, -u — только неповторяющиеся, -i — игнорировать регистр.
    """
    flags, operands = split_options(args, "cdui")
    if not operands:
        raise CommandError("missing file operand")
    if operands[1:]:
        raise CommandError(f"extra operand '{operands[1]}'")
    lines = read_lines(vfs, operands[0])
    groups = group_lines(lines, "i" in flags)
    result = []
    for line, count in select_groups(groups, flags):
        result.append(f"{count:>7} {line}" if "c" in flags else line)
    return "\n".join(result)
