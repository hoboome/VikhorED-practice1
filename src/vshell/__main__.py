"""Запуск эмулятора: ``python3 -m vshell [-v ZIP] [-s FILE] [-c]``."""

import getpass
import sys

from .interpreter import Interpreter
from .memfs import MemoryFS, VfsLoadError, load_zip
from .settings import read_settings
from .startup import run_startup


def prepare_fs(settings, user):
    """Загрузить VFS; вернуть (VFS, текст ошибки или None)."""
    if not settings.vfs_path:
        return MemoryFS(owner=user), None
    try:
        return load_zip(settings.vfs_path, user), None
    except VfsLoadError as problem:
        message = f"vshell: ошибка загрузки VFS: {problem}"
        return MemoryFS(owner=user), message


def open_terminal(settings, fs):
    """Создать окно или консольный терминал."""
    def factory(output):
        return Interpreter(output, fs)

    if settings.console:
        from .console import ConsoleTerminal
        return ConsoleTerminal(factory)
    from .window import TerminalWindow
    return TerminalWindow(factory, fs.name)


def main(argv=None):
    """Точка входа. Возвращает код завершения."""
    settings = read_settings(argv)
    if not settings.console:
        print("\n".join(settings.report()))
    fs, problem = prepare_fs(settings, getpass.getuser())
    terminal = open_terminal(settings, fs)
    for line in settings.report():
        terminal.note(line)
    if problem:
        terminal.error(problem)
    if settings.script_path:
        run_startup(terminal, settings.script_path)
    if not terminal.shell.running:
        return terminal.exit_code
    return terminal.mainloop()


if __name__ == "__main__":
    sys.exit(main())
