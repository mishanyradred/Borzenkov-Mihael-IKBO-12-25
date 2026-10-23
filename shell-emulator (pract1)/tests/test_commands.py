"""Тесты реестра команд эмулятора."""

import unittest

from src.commands import execute
from src.errors import CommandError, ExitRequested
from src.vfs import VFS


class ExecuteTests(unittest.TestCase):
    """Проверки функции execute."""

    def test_unknown_command(self):
        """Неизвестная команда вызывает CommandError."""
        with self.assertRaises(CommandError) as context:
            execute(VFS(), ["pwd"])
        self.assertEqual(str(context.exception), "pwd: command not found")

    def test_empty_tokens(self):
        """Пустой список токенов ничего не выводит."""
        self.assertEqual(execute(VFS(), []), "")

    def test_exit(self):
        """exit бросает ExitRequested."""
        with self.assertRaises(ExitRequested):
            execute(VFS(), ["exit"])

    def test_error_has_command_name(self):
        """К сообщению об ошибке добавляется имя команды."""
        with self.assertRaises(CommandError) as context:
            execute(VFS(), ["cd", "/nope"])
        self.assertEqual(
            str(context.exception), "cd: /nope: No such file or directory"
        )


if __name__ == "__main__":
    unittest.main()
