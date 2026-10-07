"""Тесты прототипа: разбор строки, заглушки, exit, ошибки."""

import unittest

from vshell.interpreter import Interpreter
from vshell.io import BufferOutput
from vshell.lexer import split_command, tokenize
from fixture_case import FixtureCase


class LexerTests(FixtureCase):
    """Разбор строки по пробелам."""

    def test_split_by_spaces(self):
        """Любое количество пробелов и табуляций — разделитель."""
        self.assertEqual(tokenize("  ls   -l\t/home "), ["ls", "-l", "/home"])

    def test_command_and_arguments(self):
        """Первое слово — команда, остальные — аргументы."""
        self.assertEqual(split_command("cd /tmp x"), ("cd", ["/tmp", "x"]))

    def test_empty(self):
        """Пустая строка не содержит команды."""
        self.assertEqual(split_command("   "), (None, []))


class PrototypeTests(FixtureCase):
    """Поведение интерпретатора на первом этапе."""

    def prepare(self):
        """Интерпретатор с буферным выводом."""
        self.out = BufferOutput()
        self.shell = Interpreter(self.out, user="lena")

    def test_prompt(self):
        """Приглашение содержит пользователя и каталог."""
        self.assertEqual(self.shell.prompt(), "lena@vshell:/$ ")

    def test_unknown_command(self):
        """Неизвестная команда — сообщение об ошибке."""
        self.assertFalse(self.shell.execute("foo 1 2"))
        self.assertEqual(self.out.lines("err"), ["foo: command not found"])

    def test_exit(self):
        """exit завершает работу с кодом."""
        self.shell.execute("exit 4")
        self.assertEqual(self.out.exit_code, 4)
        self.assertFalse(self.shell.running)

    def test_exit_errors(self):
        """exit с неверными аргументами не завершает работу."""
        self.assertFalse(self.shell.execute("exit x"))
        self.assertFalse(self.shell.execute("exit 1 2"))
        self.assertIsNone(self.out.exit_code)


if __name__ == "__main__":
    unittest.main()
