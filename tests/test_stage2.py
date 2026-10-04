"""Тесты параметров запуска и стартового скрипта."""

import io
import os
import tempfile
import unittest

from vshell.console import ConsoleTerminal
from vshell.interpreter import Interpreter
from vshell.settings import read_settings
from vshell.startup import run_startup


def make_terminal():
    """Консольный терминал, пишущий в строковый буфер."""
    stream = io.StringIO()
    terminal = ConsoleTerminal(
        lambda output: Interpreter(output, user="lena"), stream)
    return terminal, stream


class SettingsTests(unittest.TestCase):
    """Разбор параметров командной строки."""

    def test_defaults(self):
        """По умолчанию параметры не заданы."""
        settings = read_settings([])
        self.assertIsNone(settings.vfs_path)
        self.assertIsNone(settings.script_path)
        self.assertFalse(settings.console)

    def test_short_and_long(self):
        """Поддерживаются короткие и длинные формы."""
        short = read_settings(["-v", "a.zip", "-s", "b.vsh", "-c"])
        long = read_settings(["--vfs", "a.zip", "--script", "b.vsh",
                              "--console"])
        self.assertEqual(short, long)
        self.assertEqual(short.vfs_path, "a.zip")

    def test_report(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(read_settings(["-v", "x.zip"]).report())
        for name in ("vfs_path", "script_path", "console", "x.zip"):
            self.assertIn(name, text)


class StartupTests(unittest.TestCase):
    """Выполнение стартового скрипта."""

    def script(self, text):
        """Создать временный скрипт и вернуть путь."""
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".vsh", delete=False, encoding="utf-8")
        with handle:
            handle.write(text)
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_dialog_and_skipping(self):
        """Ввод виден, ошибочные строки пропускаются."""
        terminal, stream = make_terminal()
        path = self.script("# comment\nls\nbad\n\ncd /\n")
        self.assertEqual(run_startup(terminal, path), [3])
        text = stream.getvalue()
        self.assertIn("lena@vshell:/$ ls", text)
        self.assertIn("bad: command not found", text)
        self.assertIn("lena@vshell:/$ cd /", text)

    def test_exit_stops_script(self):
        """exit останавливает скрипт."""
        terminal, stream = make_terminal()
        run_startup(terminal, self.script("exit 2\nls\n"))
        self.assertEqual(terminal.exit_code, 2)
        self.assertNotIn("$ ls", stream.getvalue())

    def test_missing_script(self):
        """Отсутствующий скрипт — сообщение об ошибке."""
        terminal, stream = make_terminal()
        run_startup(terminal, "/no/such.vsh")
        self.assertIn("cannot run script", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
