"""Тесты команд эмулятора."""

import unittest

from src.commands import ExitRequested, execute


class ExecuteTests(unittest.TestCase):
    """Проверки функции execute."""

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(execute(["ls", "-l"]), "ls: args=['-l']")

    def test_cd_stub(self):
        """cd выводит своё имя и аргументы."""
        self.assertEqual(execute(["cd", "/"]), "cd: args=['/']")

    def test_unknown_command(self):
        """Неизвестная команда даёт сообщение об ошибке."""
        self.assertIn("not found", execute(["pwd"]))

    def test_empty_tokens(self):
        """Пустой список токенов ничего не выводит."""
        self.assertEqual(execute([]), "")

    def test_exit(self):
        """exit бросает ExitRequested."""
        with self.assertRaises(ExitRequested):
            execute(["exit"])


if __name__ == "__main__":
    unittest.main()
