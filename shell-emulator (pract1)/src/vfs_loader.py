"""Загрузка VFS из CSV-файла.

Формат: заголовок ``path,type,content``; path — абсолютный путь,
type — ``dir`` или ``file``, content — содержимое файла в base64.
Вложенность задаётся полным путём, родитель должен присутствовать
в файле (порядок строк не важен).
"""

import base64
import csv

from src.errors import VFSError
from src.vfs import VFS, Node

HEADER = ["path", "type", "content"]
TYPE_DIR = "dir"
TYPE_FILE = "file"


def read_rows(path):
    """Читает CSV и возвращает пары (номер строки, поля) без заголовка."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            rows = [(reader.line_num, row) for row in reader]
    except OSError as error:
        raise VFSError(error.strerror or str(error)) from error
    except UnicodeDecodeError as error:
        raise VFSError("invalid format: not a UTF-8 text file") from error
    except csv.Error as error:
        raise VFSError(f"invalid format: {error}") from error
    if not rows or rows[0][1] != HEADER:
        raise VFSError("invalid format: expected header 'path,type,content'")
    return rows[1:]


def split_path(raw_path):
    """Делит абсолютный путь из CSV на список имён."""
    if not raw_path.startswith("/"):
        raise VFSError("path must be absolute")
    parts = [part for part in raw_path.split("/") if part not in ("", ".")]
    if ".." in parts:
        raise VFSError("path must not contain '..'")
    return parts


def decode_content(text):
    """Декодирует содержимое файла из base64."""
    try:
        return base64.b64decode(text, validate=True)
    except ValueError as error:
        raise VFSError("invalid base64 content") from error


def parse_row(row):
    """Превращает строку CSV в пару (список имён, узел)."""
    if len(row) != len(HEADER):
        raise VFSError(f"expected {len(HEADER)} columns, got {len(row)}")
    raw_path, kind, content = row
    parts = split_path(raw_path)
    name = parts[-1] if parts else ""
    kind = kind.strip()
    if kind == TYPE_DIR:
        if content:
            raise VFSError("directory must not have content")
        return parts, Node(name, True)
    if kind != TYPE_FILE:
        raise VFSError(f"unknown type '{kind}'")
    if not parts:
        raise VFSError("root must be a directory")
    return parts, Node(name, False, decode_content(content))


def parse_rows(rows):
    """Разбирает все строки; пустые пропускает, ошибки снабжает номером."""
    items = []
    for number, row in rows:
        if not row:
            continue
        try:
            parts, node = parse_row(row)
        except VFSError as error:
            raise VFSError(f"line {number}: {error}") from error
        items.append((number, row[0], parts, node))
    return items


def build_vfs(rows):
    """Собирает дерево VFS из строк CSV."""
    vfs = VFS()
    for number, raw_path, parts, node in sorted(
        parse_rows(rows), key=lambda item: len(item[2])
    ):
        if not parts:
            continue
        try:
            vfs.add(parts, node)
        except VFSError as error:
            message = f"line {number}: '{raw_path}': {error}"
            raise VFSError(message) from error
    return vfs


def load_vfs(path):
    """Загружает VFS из CSV-файла в память.

    Бросает VFSError, если файл не найден или имеет неверный формат.
    """
    try:
        return build_vfs(read_rows(path))
    except VFSError as error:
        raise VFSError(f"{path}: {error}") from error
