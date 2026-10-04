"""Работа эмулятора в обычной консоли (параметр --console)."""

import sys

from .io import Output


class ConsoleTerminal(Output):
    """Терминал на стандартных потоках ввода и вывода."""

    def __init__(self, interpreter_factory, stream=None):
        """Создать терминал и интерпретатор для него."""
        self.stream = stream or sys.stdout
        self.exit_code = 0
        self.shell = interpreter_factory(self)

    def emit(self, text, style):
        """Напечатать строку."""
        print(text, file=self.stream, flush=True)

    def shutdown(self, code):
        """Запомнить код завершения."""
        self.exit_code = code

    def run_line(self, line, echo=True):
        """Показать строку с приглашением и выполнить её."""
        if echo:
            self.emit(self.shell.prompt() + line, "cmd")
        return self.shell.execute(line)

    def mainloop(self, source=None):
        """Читать команды из ``source`` (по умолчанию stdin) до EOF."""
        source = source or sys.stdin
        while self.shell.running:
            line = source.readline()
            if not line:
                break
            self.run_line(line.rstrip("\n"))
        return self.exit_code
