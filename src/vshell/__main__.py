"""Запуск эмулятора: ``python3 -m vshell [-v ZIP] [-s FILE] [-c]``."""

import sys

from .interpreter import Interpreter
from .settings import read_settings
from .startup import run_startup


def open_terminal(settings, vfs_name):
    """Создать окно или консольный терминал."""
    def factory(output):
        return Interpreter(output, vfs_name)

    if settings.console:
        from .console import ConsoleTerminal
        return ConsoleTerminal(factory)
    from .window import TerminalWindow
    return TerminalWindow(factory, vfs_name)


def main(argv=None):
    """Точка входа. Возвращает код завершения."""
    settings = read_settings(argv)
    if not settings.console:
        print("\n".join(settings.report()))
    vfs_name = settings.vfs_path or "empty"
    terminal = open_terminal(settings, vfs_name)
    for line in settings.report():
        terminal.note(line)
    if settings.script_path:
        run_startup(terminal, settings.script_path)
    if not terminal.shell.running:
        return terminal.exit_code
    return terminal.mainloop()


if __name__ == "__main__":
    sys.exit(main())
