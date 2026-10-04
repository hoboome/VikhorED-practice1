"""Тесты команд-заглушек первого этапа."""

import unittest

from vshell.interpreter import Interpreter
from vshell.io import BufferOutput


class StubTests(unittest.TestCase):
    """ls и cd выводят своё имя и аргументы."""

    def test_stubs(self):
        """Заглушки печатают имя и список аргументов."""
        out = BufferOutput()
        shell = Interpreter(out, user="lena")
        shell.execute("ls -l /home")
        shell.execute("cd /tmp")
        self.assertEqual(out.lines(), ["[stub] ls ['-l', '/home']",
                                       "[stub] cd ['/tmp']"])


if __name__ == "__main__":
    unittest.main()
