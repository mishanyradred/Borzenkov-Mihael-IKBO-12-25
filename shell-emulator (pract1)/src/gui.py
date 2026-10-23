"""Графический интерфейс эмулятора."""

import tkinter as tk

from src.commands import ExitRequested, execute
from src.parser import ParseError, parse_line

PROMPT = "$ "
OUTPUT_HEIGHT = 24
OUTPUT_WIDTH = 80


class EmulatorWindow:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, vfs_name):
        """Создаёт окно с заголовком, содержащим имя VFS."""
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{vfs_name}]")
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

    def on_enter(self, _event):
        """Обрабатывает нажатие Enter: разбирает и выполняет команду."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(PROMPT + line)
        try:
            result = execute(parse_line(line))
        except ParseError as error:
            result = f"error: {error}"
        except ExitRequested:
            self.root.destroy()
            return
        if result:
            self.write(result)

    def run(self):
        """Запускает главный цикл окна."""
        self.root.mainloop()
