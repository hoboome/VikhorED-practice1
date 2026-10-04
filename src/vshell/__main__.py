"""Запуск эмулятора: ``python3 -m vshell``."""

import sys

from .interpreter import Interpreter
from .window import TerminalWindow


def main():
    """Открыть окно эмулятора и вернуть код завершения."""
    vfs_name = "empty"
    window = TerminalWindow(
        lambda output: Interpreter(output, vfs_name), vfs_name)
    return window.mainloop()


if __name__ == "__main__":
    sys.exit(main())
