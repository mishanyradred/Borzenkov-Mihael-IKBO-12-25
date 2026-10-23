"""Графический интерфейс эмулятора."""

import tkinter as tk

from src.commands import execute
from src.config import describe, vfs_title
from src.errors import EmulatorError, ExitRequested, ParseError, VFSError
from src.parser import parse_line
from src.script import ScriptError, read_script
from src.vfs import VFS
from src.vfs_loader import load_vfs

PROMPT = "$ "
OUTPUT_HEIGHT = 24
OUTPUT_WIDTH = 80


def format_error(error, line_no=None):
    """Формирует сообщение об ошибке для вывода в окне.

    Если указан номер строки, ошибка относится к стартовому скрипту.
    """
    if line_no is not None:
        return f"script error (line {line_no}): {error}"
    if isinstance(error, ParseError):
        return f"error: {error}"
    return str(error)


class EmulatorWindow:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, config):
        """Создаёт окно с заголовком, содержащим имя VFS."""
        self.config = config
        self.vfs = VFS()
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{vfs_title(config)}]")
        self.output = tk.Text(
            self.root,
            height=OUTPUT_HEIGHT,
            width=OUTPUT_WIDTH,
            state="disabled",
        )
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(self.root)
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

    def write(self, text):
        """Добавляет строку в область вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def handle_line(self, line, line_no=None):
        """Показывает и выполняет строку.

        Возвращает False, если запрошен выход из эмулятора.
        """
        self.write(PROMPT + line)
        try:
            result = execute(parse_line(line))
        except EmulatorError as error:
            self.write(format_error(error, line_no))
            return True
        except ExitRequested:
            return False
        if result:
            self.write(result)
        return True

    def on_enter(self, _event):
        """Обрабатывает нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        if not self.handle_line(line):
            self.root.destroy()

    def load_vfs(self):
        """Загружает VFS из файла, заданного параметром --vfs.

        При ошибке сообщает о ней и возвращает пустую VFS.
        """
        path = self.config.vfs_path
        if not path:
            return VFS()
        try:
            vfs = load_vfs(path)
        except VFSError as error:
            self.write(f"vfs error: {error}")
            return VFS()
        self.write(f"[vfs] загружено узлов: {vfs.root.descendants()}")
        return vfs

    def run_startup_script(self):
        """Выполняет стартовый скрипт, имитируя диалог с пользователем.

        Ошибка в строке скрипта не прерывает выполнение остальных строк.
        Возвращает False, если скрипт запросил выход.
        """
        try:
            lines = read_script(self.config.script_path)
        except ScriptError as error:
            self.write(f"script error: {error}")
            return True
        for number, line in lines:
            if not self.handle_line(line, number):
                return False
        return True

    def start(self):
        """Выводит параметры, загружает VFS, выполняет стартовый скрипт."""
        for text in describe(self.config):
            self.write(text)
        self.vfs = self.load_vfs()
        if self.config.script_path and not self.run_startup_script():
            self.root.destroy()

    def run(self):
        """Запускает главный цикл окна."""
        self.root.after(0, self.start)
        self.root.mainloop()
