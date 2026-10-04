"""Настройки запуска эмулятора из параметров командной строки."""

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """Параметры запуска."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None
    console: bool = False

    def report(self):
        """Строки отладочного вывода всех параметров."""
        return [
            "debug: параметры запуска",
            f"debug:   vfs_path    = {self.vfs_path!r}",
            f"debug:   script_path = {self.script_path!r}",
            f"debug:   console     = {self.console!r}",
        ]


def make_parser():
    """Описать параметры командной строки."""
    parser = argparse.ArgumentParser(
        prog="vshell", description="Эмулятор командной оболочки UNIX")
    parser.add_argument("-v", "--vfs", dest="vfs_path", metavar="ZIP",
                        help="путь к ZIP-архиву с VFS")
    parser.add_argument("-s", "--script", dest="script_path",
                        metavar="FILE", help="путь к стартовому скрипту")
    parser.add_argument("-c", "--console", action="store_true",
                        help="работать в консоли без окна")
    return parser


def read_settings(argv=None):
    """Разобрать параметры командной строки."""
    namespace = make_parser().parse_args(argv)
    return Settings(**vars(namespace))
