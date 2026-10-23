"""Тесты команд ls, cd и du."""

import unittest

from src.cmd_fs import human_size
from src.errors import CommandError
from tests.helpers import deep_vfs, run


class LsTests(unittest.TestCase):
    """Проверки команды ls."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_root(self):
        """ls без аргументов показывает текущую папку."""
        self.assertEqual(run(self.vfs, "ls"), "bin\netc\nhome\ntmp")

    def test_hidden_files(self):
        """Скрытые файлы видны только с -a."""
        self.assertEqual(run(self.vfs, "ls /home/user"), "docs\nnotes.txt")
        self.assertEqual(
            run(self.vfs, "ls -a /home/user"), ".profile\ndocs\nnotes.txt"
        )

    def test_long_format(self):
        """Флаг -l добавляет тип и размер."""
        lines = run(self.vfs, "ls -l /home/user").splitlines()
        self.assertTrue(lines[0].startswith("d "))
        self.assertTrue(lines[1].endswith(" 46 notes.txt"))

    def test_file_argument(self):
        """ls для файла выводит его путь."""
        self.assertEqual(run(self.vfs, "ls /etc/hosts"), "/etc/hosts")

    def test_several_paths(self):
        """Для нескольких путей выводятся заголовки."""
        text = run(self.vfs, "ls /etc /bin")
        self.assertEqual(text, "/etc:\nhosts\n\n/bin:\ntool.bin")

    def test_relative_after_cd(self):
        """Относительный путь считается от текущей папки."""
        run(self.vfs, "cd /home/user")
        self.assertEqual(
            run(self.vfs, "ls docs"), "empty.txt\nreadme.txt\nwork"
        )
        self.assertEqual(run(self.vfs, "ls .."), "user")

    def test_empty_dir(self):
        """Пустая папка даёт пустой вывод."""
        self.assertEqual(run(self.vfs, "ls /tmp"), "")

    def test_missing_path(self):
        """Несуществующий путь вызывает CommandError."""
        with self.assertRaises(CommandError):
            run(self.vfs, "ls /nope")

    def test_invalid_option(self):
        """Неизвестный флаг вызывает CommandError."""
        with self.assertRaises(CommandError):
            run(self.vfs, "ls -z")


class CdTests(unittest.TestCase):
    """Проверки команды cd."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_absolute_and_relative(self):
        """cd работает с абсолютными и относительными путями."""
        run(self.vfs, "cd /home/user")
        self.assertEqual(self.vfs.pwd(), "/home/user")
        run(self.vfs, "cd docs/work")
        self.assertEqual(self.vfs.pwd(), "/home/user/docs/work")
        run(self.vfs, "cd ../..")
        self.assertEqual(self.vfs.pwd(), "/home/user")

    def test_no_argument(self):
        """cd без аргумента переходит в корень."""
        run(self.vfs, "cd /etc")
        run(self.vfs, "cd")
        self.assertEqual(self.vfs.pwd(), "/")

    def test_missing(self):
        """cd в несуществующую папку вызывает CommandError."""
        with self.assertRaises(CommandError):
            run(self.vfs, "cd /nope")

    def test_into_file(self):
        """cd в файл вызывает CommandError."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cd /etc/hosts")
        self.assertIn("Not a directory", str(context.exception))

    def test_too_many_arguments(self):
        """Лишние аргументы вызывают CommandError."""
        with self.assertRaises(CommandError):
            run(self.vfs, "cd /etc /bin")


class DuTests(unittest.TestCase):
    """Проверки команды du."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_summary(self):
        """-s выводит только итог."""
        self.assertEqual(run(self.vfs, "du -s /home/user"), "98\t/home/user")

    def test_directories(self):
        """Без флагов выводятся вложенные папки и итог."""
        self.assertEqual(
            run(self.vfs, "du /home/user/docs"),
            "23\t/home/user/docs/work\n35\t/home/user/docs",
        )

    def test_all_files(self):
        """-a добавляет файлы."""
        self.assertEqual(
            run(self.vfs, "du -a /etc"), "20\t/etc/hosts\n20\t/etc"
        )

    def test_file(self):
        """Для файла выводится его размер."""
        self.assertEqual(run(self.vfs, "du /etc/hosts"), "20\t/etc/hosts")

    def test_human_readable(self):
        """-h выводит размеры с единицами."""
        self.assertEqual(run(self.vfs, "du -sh /bin"), "5B\t/bin")

    def test_current_dir(self):
        """Без пути берётся текущая папка."""
        run(self.vfs, "cd /etc")
        self.assertEqual(run(self.vfs, "du -s"), "20\t.")

    def test_missing_path(self):
        """Несуществующий путь вызывает CommandError."""
        with self.assertRaises(CommandError):
            run(self.vfs, "du /nope")

    def test_human_size_units(self):
        """human_size подбирает единицу измерения."""
        self.assertEqual(human_size(0), "0B")
        self.assertEqual(human_size(1536), "1.5K")
        self.assertEqual(human_size(1048576), "1.0M")


if __name__ == "__main__":
    unittest.main()
