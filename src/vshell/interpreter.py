"""Интерпретатор команд эмулятора."""

import getpass

from .errors import CommandError
from .lexer import split_command
from .memfs import MemoryFS
from .navigation import NavigationCommands
from .session import SessionCommands
from .textutils import TextCommands

HOST = "vshell"

__all__ = ["CommandError", "Interpreter"]


class Interpreter(NavigationCommands, TextCommands, SessionCommands):
    """Выполняет строки ввода и выводит результат в ``Output``.

    Команда ``name`` реализуется методом ``cmd_name(self, args)``
    в одном из классов-примесей. Метод сообщает о неудаче исключением
    ``CommandError`` или возвратом ``False``.
    """

    def __init__(self, output, fs=None, user=None):
        """Связать интерпретатор с выводом ``output`` и VFS ``fs``."""
        self.output = output
        self.user = user or getpass.getuser()
        self.fs = fs or MemoryFS(owner=self.user)
        self.cwd = "/"
        self.previous = None
        self.history = []
        self.running = True

    def prompt(self):
        """Строка приглашения: ``user@vshell:путь$``."""
        home = self.home()
        shown = self.cwd
        if home != "/" and (shown == home or shown.startswith(home + "/")):
            shown = "~" + shown[len(home):]
        return f"{self.user}@{HOST}:{shown}$ "

    def handler(self, name):
        """Найти метод команды по имени или вернуть None."""
        return getattr(self, "cmd_" + name, None)

    def execute(self, line):
        """Выполнить одну строку. Вернуть True при успехе."""
        name, args = split_command(line)
        if name is None:
            return True
        self.history.append(line.strip())
        method = self.handler(name)
        if method is None:
            self.output.error(f"{name}: command not found")
            return False
        try:
            return method(args) is not False
        except CommandError as problem:
            self.output.error(str(problem))
            return False
