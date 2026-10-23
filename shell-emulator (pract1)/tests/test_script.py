"""Тесты чтения стартового скрипта."""

import os
import tempfile
import unittest

from src.script import ScriptError, read_script


class ReadScriptTests(unittest.TestCase):
    """Проверки функции read_script."""

    def test_skips_blank_lines(self):
        """Пустые строки пропускаются, номера строк сохраняются."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "s.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("ls\n\n# note\ncd /\n")
            self.assertEqual(
                read_script(path),
                [(1, "ls"), (3, "# note"), (4, "cd /")],
            )

    def test_missing_file(self):
        """Отсутствующий файл вызывает ScriptError."""
        with self.assertRaises(ScriptError):
            read_script("/no/such/script.txt")

    def test_binary_file(self):
        """Не UTF-8 файл вызывает ScriptError."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "s.bin")
            with open(path, "wb") as file:
                file.write(b"\xff\xfe\x00\x80")
            with self.assertRaises(ScriptError):
                read_script(path)


if __name__ == "__main__":
    unittest.main()
