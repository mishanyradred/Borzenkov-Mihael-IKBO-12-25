"""Точка входа эмулятора."""

from src.gui import EmulatorWindow

VFS_NAME = "vfs"


def main():
    """Запускает окно эмулятора."""
    EmulatorWindow(VFS_NAME).run()


if __name__ == "__main__":
    main()
