"""Тесты разбора командной строки."""

import os
import unittest

from src.parser import ParseError, parse_line


class ParseLineTests(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_splits_arguments(self):
        """Строка делится на команду и аргументы."""
        self.assertEqual(parse_line("ls -l /tmp"), ["ls", "-l", "/tmp"])

    def test_quotes_keep_spaces(self):
        """Кавычки сохраняют пробелы внутри аргумента."""
        self.assertEqual(parse_line('ls "my dir"'), ["ls", "my dir"])

    def test_expands_env(self):
        """Переменные окружения раскрываются."""
        os.environ["EMU_TEST"] = "/value"
        self.assertEqual(parse_line("cd $EMU_TEST"), ["cd", "/value"])

    def test_empty_line(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse_line(""), [])

    def test_unclosed_quote(self):
        """Незакрытая кавычка вызывает ParseError."""
        with self.assertRaises(ParseError):
            parse_line('ls "oops')

    def test_comment_line(self):
        """Строка-комментарий даёт пустой список."""
        self.assertEqual(parse_line("# просто комментарий"), [])

    def test_inline_comment(self):
        """Комментарий в конце строки отбрасывается."""
        self.assertEqual(parse_line("ls /tmp # список"), ["ls", "/tmp"])

    def test_hash_in_quotes(self):
        """Символ # внутри кавычек не начинает комментарий."""
        self.assertEqual(parse_line('ls "a#b"'), ["ls", "a#b"])


if __name__ == "__main__":
    unittest.main()
