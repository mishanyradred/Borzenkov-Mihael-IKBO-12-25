"""Исключения эмулятора."""


class EmulatorError(Exception):
    """Базовая ошибка эмулятора: сообщение показывается пользователю."""


class ParseError(EmulatorError):
    """Ошибка разбора командной строки."""


class CommandError(EmulatorError):
    """Ошибка выполнения команды."""


class VFSError(EmulatorError):
    """Ошибка загрузки или использования виртуальной файловой системы."""


class ExitRequested(Exception):
    """Сигнал о том, что пользователь запросил выход."""
