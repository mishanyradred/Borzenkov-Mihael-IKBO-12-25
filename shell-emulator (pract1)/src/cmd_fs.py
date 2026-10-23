"""Команды работы с файловой системой: ls, cd, du, mkdir, cp."""

import posixpath

from src.errors import CommandError
from src.options import split_options

BASE = 1024
UNITS = "BKMG"
ROOT_PATH = "/"
CURRENT_DIR = "."


def by_name(node):
    """Ключ сортировки узлов по имени."""
    return node.name


def format_entry(node, name, long_format):
    """Форматирует строку вывода ls для одного узла."""
    if not long_format:
        return name
    kind = "d" if node.is_dir else "-"
    return f"{kind} {node.size:>8} {name}"


def list_target(vfs, path, flags):
    """Возвращает строки вывода ls для одного пути."""
    node = vfs.get(path)
    long_format = "l" in flags
    if not node.is_dir:
        return [format_entry(node, path, long_format)]
    entries = sorted(node.children.values(), key=by_name)
    if "a" not in flags:
        entries = [n for n in entries if not n.name.startswith(".")]
    return [format_entry(n, n.name, long_format) for n in entries]


def cmd_ls(vfs, args):
    """ls [-l] [-a] [путь...]: содержимое папки или сведения о файле.

    -l — подробный формат (тип, размер, имя), -a — показывать скрытые
    файлы (имя начинается с точки). Без пути берётся текущая папка.
    """
    flags, paths = split_options(args, "la")
    targets = paths or [CURRENT_DIR]
    if not targets[1:]:
        return "\n".join(list_target(vfs, targets[0], flags))
    blocks = [
        f"{path}:\n" + "\n".join(list_target(vfs, path, flags))
        for path in targets
    ]
    return "\n\n".join(blocks)


def cmd_cd(vfs, args):
    """cd [путь]: сменить текущую папку; без пути — перейти в корень."""
    if args[1:]:
        raise CommandError("too many arguments")
    vfs.change_dir(args[0] if args else ROOT_PATH)
    return ""


def format_size(value, unit):
    """Форматирует число с единицей измерения."""
    if unit == UNITS[0]:
        return f"{int(value)}{unit}"
    return f"{value:.1f}{unit}"


def human_size(size):
    """Переводит размер в байтах в вид 1.5K, 2.0M и так далее."""
    value = float(size)
    for unit in UNITS[:-1]:
        if value < BASE:
            return format_size(value, unit)
        value /= BASE
    return format_size(value, UNITS[-1])


def collect_sizes(node, path, show_files, fmt):
    """Возвращает строки du для папки: сначала вложенные, затем она."""
    lines = []
    for child in sorted(node.children.values(), key=by_name):
        child_path = posixpath.join(path, child.name)
        if child.is_dir:
            lines.extend(collect_sizes(child, child_path, show_files, fmt))
        elif show_files:
            lines.append(f"{fmt(child.size)}\t{child_path}")
    lines.append(f"{fmt(node.size)}\t{path}")
    return lines


def cmd_du(vfs, args):
    """du [-s] [-h] [-a] [путь...]: размер файлов и папок в байтах.

    -s — только итог для каждого пути, -h — человекочитаемые размеры
    (1.5K), -a — показывать и файлы, а не только папки.
    """
    flags, paths = split_options(args, "sha")
    fmt = human_size if "h" in flags else str
    lines = []
    for path in paths or [CURRENT_DIR]:
        node = vfs.get(path)
        if "s" in flags or not node.is_dir:
            lines.append(f"{fmt(node.size)}\t{path}")
        else:
            lines.extend(collect_sizes(node, path, "a" in flags, fmt))
    return "\n".join(lines)


def cmd_mkdir(vfs, args):
    """mkdir [-p] путь...: создать папки в памяти.

    -p — создавать недостающих родителей, не считать ошибкой уже
    существующую папку.
    """
    flags, paths = split_options(args, "p")
    if not paths:
        raise CommandError("missing operand")
    for path in paths:
        vfs.make_dir(path, parents="p" in flags)
    return ""


def cmd_cp(vfs, args):
    """cp [-r] источник... назначение: копировать в памяти.

    Файл копируется под новым именем, перезаписывая существующий, или
    внутрь папки-назначения. Для папки нужен -r. Несколько источников
    допустимы, только если назначение — папка.
    """
    flags, operands = split_options(args, "r")
    if not operands:
        raise CommandError("missing file operand")
    if not operands[1:]:
        message = f"missing destination file operand after '{operands[0]}'"
        raise CommandError(message)
    *sources, dest = operands
    if sources[1:] and not vfs.is_dir(dest):
        raise CommandError(f"target '{dest}' is not a directory")
    for source in sources:
        vfs.copy(source, dest, "r" in flags)
    return ""
