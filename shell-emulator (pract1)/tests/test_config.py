"""Тесты параметров командной строки."""

import unittest

from src.config import Config, describe, parse_args, vfs_title


class ParseArgsTests(unittest.TestCase):
    """Проверки разбора аргументов."""

    def test_no_arguments(self):
        """Без аргументов оба параметра не заданы."""
        self.assertEqual(parse_args([]), Config())

    def test_both_arguments(self):
        """Оба параметра попадают в Config."""
        config = parse_args(["--vfs", "a.csv", "--script", "s.txt"])
        self.assertEqual(config, Config("a.csv", "s.txt"))

    def test_unknown_argument(self):
        """Неизвестный параметр завершает разбор ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--nope"])


class DescribeTests(unittest.TestCase):
    """Проверки отладочного вывода и заголовка."""

    def test_describe_lists_all_params(self):
        """Отладочный вывод содержит оба параметра."""
        text = "\n".join(describe(Config("a.csv", "s.txt")))
        self.assertIn("a.csv", text)
        self.assertIn("s.txt", text)

    def test_describe_not_set(self):
        """Незаданные параметры помечаются."""
        self.assertIn("не задан", "\n".join(describe(Config())))

    def test_title_from_path(self):
        """В заголовок попадает имя файла VFS."""
        self.assertEqual(vfs_title(Config("dir/big.csv")), "big.csv")

    def test_title_default(self):
        """Без пути используется имя по умолчанию."""
        self.assertEqual(vfs_title(Config()), "vfs")


if __name__ == "__main__":
    unittest.main()
