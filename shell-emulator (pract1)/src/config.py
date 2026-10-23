"""Параметры командной строки эмулятора."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_VFS_NAME = "vfs"
NOT_SET = "(не задан)"


@dataclass
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None


def parse_args(argv=None):
    """Разбирает аргументы командной строки и возвращает Config."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки UNIX с виртуальной файловой системой.",
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        help="путь к стартовому скрипту",
    )
    args = parser.parse_args(argv)
    return Config(vfs_path=args.vfs_path, script_path=args.script_path)


def describe(config):
    """Возвращает строки отладочного вывода всех заданных параметров."""
    return [
        "[debug] параметры запуска:",
        f"[debug]   --vfs    = {config.vfs_path or NOT_SET}",
        f"[debug]   --script = {config.script_path or NOT_SET}",
    ]


def vfs_title(config):
    """Возвращает имя VFS для заголовка окна."""
    if config.vfs_path:
        return os.path.basename(config.vfs_path)
    return DEFAULT_VFS_NAME
