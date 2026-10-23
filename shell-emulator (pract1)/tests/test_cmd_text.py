"""Тесты команды uniq."""

import unittest

from src.errors import CommandError
from tests.helpers import deep_vfs, run

NOTES = "/home/user/notes.txt"


class UniqTests(unittest.TestCase):
    """Проверки команды uniq."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_plain(self):
        """Соседние повторы склеиваются, несоседние остаются."""
        self.assertEqual(
            run(self.vfs, f"uniq {NOTES}"),
            "apple\nbanana\napple\nCherry\ncherry",
        )

    def test_count(self):
        """-c выводит число повторов."""
        lines = run(self.vfs, f"uniq -c {NOTES}").splitlines()
        self.assertEqual(lines[0], "      2 apple")
        self.assertEqual(lines[1], "      1 banana")

    def test_duplicates_only(self):
        """-d оставляет только повторяющиеся строки."""
        self.assertEqual(run(self.vfs, f"uniq -d {NOTES}"), "apple\ncherry")

    def test_unique_only(self):
        """-u оставляет только неповторяющиеся строки."""
        self.assertEqual(
            run(self.vfs, f"uniq -u {NOTES}"), "banana\napple\nCherry"
        )

    def test_ignore_case(self):
        """-i игнорирует регистр."""
        self.assertEqual(
            run(self.vfs, f"uniq -ic {NOTES}").splitlines()[-1],
            "      3 Cherry",
        )

    def test_empty_file(self):
        """Пустой файл даёт пустой вывод."""
        self.assertEqual(run(self.vfs, "uniq /home/user/docs/empty.txt"), "")

    def test_missing_operand(self):
        """Без файла команда завершается ошибкой."""
        with self.assertRaises(CommandError):
            run(self.vfs, "uniq")

    def test_extra_operand(self):
        """Лишний операнд вызывает ошибку."""
        with self.assertRaises(CommandError):
            run(self.vfs, f"uniq {NOTES} {NOTES}")

    def test_missing_file(self):
        """Несуществующий файл вызывает ошибку."""
        with self.assertRaises(CommandError):
            run(self.vfs, "uniq /nope.txt")

    def test_directory(self):
        """Папка вместо файла вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "uniq /etc")
        self.assertIn("Is a directory", str(context.exception))

    def test_binary_file(self):
        """Двоичный файл вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "uniq /bin/tool.bin")
        self.assertIn("not a text file", str(context.exception))


if __name__ == "__main__":
    unittest.main()
