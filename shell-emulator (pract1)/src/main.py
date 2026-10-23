"""Точка входа эмулятора."""

from src.config import parse_args
from src.gui import EmulatorWindow


def main(argv=None):
    """Разбирает параметры и запускает окно эмулятора."""
    config = parse_args(argv)
    EmulatorWindow(config).run()


if __name__ == "__main__":
    main()
