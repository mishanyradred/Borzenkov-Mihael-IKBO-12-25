"""Тесты разбора флагов команд."""

import unittest

from src.errors import CommandError
from src.options import split_options


class SplitOptionsTests(unittest.TestCase):
    """Проверки функции split_options."""

    def test_flags_and_operands(self):
        """Флаги и операнды разделяются."""
        flags, operands = split_options(["-l", "a", "b"], "la")
        self.assertEqual(flags, {"l"})
        self.assertEqual(operands, ["a", "b"])

    def test_combined_flags(self):
        """Объединённые флаги разбираются по буквам."""
        flags, _ = split_options(["-la"], "la")
        self.assertEqual(flags, {"l", "a"})

    def test_double_dash(self):
        """После -- всё считается операндами."""
        flags, operands = split_options(["--", "-l"], "l")
        self.assertEqual(flags, set())
        self.assertEqual(operands, ["-l"])

    def test_single_dash_is_operand(self):
        """Одиночный дефис — операнд."""
        self.assertEqual(split_options(["-"], "l")[1], ["-"])

    def test_invalid_flag(self):
        """Неизвестный флаг вызывает CommandError."""
        with self.assertRaises(CommandError) as context:
            split_options(["-x"], "l")
        self.assertIn("'x'", str(context.exception))


if __name__ == "__main__":
    unittest.main()
