"""Общие вспомогательные функции тестов."""

import os

from src.commands import execute
from src.parser import parse_line
from src.vfs_loader import load_vfs

VFS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vfs")


def deep_vfs():
    """Загружает образец VFS с глубокой вложенностью."""
    return load_vfs(os.path.join(VFS_DIR, "deep.csv"))


def run(vfs, line):
    """Разбирает и выполняет строку над VFS, возвращает вывод."""
    return execute(vfs, parse_line(line))
