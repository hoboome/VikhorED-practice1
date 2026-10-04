"""Тесты основных команд: ls, cd, history, tac, clear."""

import unittest

from vshell.interpreter import Interpreter
from vshell.io import BufferOutput
from vshell.memfs import MemoryFS


def sample_fs():
    """VFS для тестов с домашним каталогом lena."""
    fs = MemoryFS(name="sample", owner="lena")
    fs.add_file("/home/lena/notes.txt", b"one\ntwo\nthree\n")
    fs.add_file("/home/lena/.secret", b"x")
    fs.add_file("/home/lena/docs/plan.txt", b"a\nb\n")
    fs.add_file("/etc/hostname", b"vshell\n")
    fs.add_file("/bin.dat", bytes([0xff, 0x0a, 0x41]))
    return fs


class CommandTestCase(unittest.TestCase):
    """Базовый класс с интерпретатором над тестовой VFS."""

    def setUp(self):
        """Интерпретатор и буферный вывод."""
        self.out = BufferOutput()
        self.shell = Interpreter(self.out, sample_fs(), user="lena")

    def run_cmd(self, line):
        """Выполнить строку и вернуть (успех, вывод, ошибки)."""
        self.out.records.clear()
        ok = self.shell.execute(line)
        return ok, self.out.lines(), self.out.lines("err")


class LsTests(CommandTestCase):
    """Команда ls."""

    def test_plain_and_hidden(self):
        """Скрытые файлы показываются только с -a."""
        self.assertEqual(self.run_cmd("ls /home/lena")[1],
                         ["docs  notes.txt"])
        self.assertEqual(self.run_cmd("ls -a /home/lena")[1],
                         [".  ..  .secret  docs  notes.txt"])

    def test_long(self):
        """ls -l показывает права, владельца, группу и размер."""
        ok, rows, _ = self.run_cmd("ls -l /home/lena")
        self.assertTrue(ok)
        self.assertEqual(rows[1], "-rw-r--r-- 1 lena lena    14 notes.txt")
        self.assertTrue(rows[0].startswith("drwxr-xr-x"))

    def test_several_and_errors(self):
        """Несколько путей; ошибка для одного не мешает остальным."""
        ok, rows, errors = self.run_cmd("ls /etc/hostname /none /etc")
        self.assertFalse(ok)
        self.assertEqual(rows, ["/etc/hostname", "/etc:", "hostname"])
        self.assertIn("cannot access '/none'", errors[0])
        self.assertIn("invalid option", self.run_cmd("ls -z")[2][0])


class CdTests(CommandTestCase):
    """Команда cd."""

    def test_moves(self):
        """Абсолютные и относительные пути, ~, -, .."""
        self.run_cmd("cd /home/lena/docs")
        self.assertEqual(self.shell.prompt(), "lena@vshell:~/docs$ ")
        self.run_cmd("cd ../..")
        self.assertEqual(self.shell.cwd, "/home")
        self.assertEqual(self.run_cmd("cd -")[1], ["/home/lena/docs"])
        self.run_cmd("cd")
        self.assertEqual(self.shell.cwd, "/home/lena")

    def test_errors(self):
        """Ошибки cd не меняют текущий каталог."""
        for line, text in (("cd /x", "No such file"),
                           ("cd /etc/hostname", "Not a directory"),
                           ("cd / /", "too many"),
                           ("cd -", "OLDPWD")):
            ok, _, errors = self.run_cmd(line)
            self.assertFalse(ok)
            self.assertIn(text, errors[0])
        self.assertEqual(self.shell.cwd, "/")


class HistoryTests(CommandTestCase):
    """Команда history."""

    def test_numbering_and_limit(self):
        """Нумерация с 1, history N — последние N команд."""
        self.run_cmd("ls")
        self.run_cmd("cd /etc")
        rows = self.run_cmd("history")[1]
        self.assertEqual(rows, ["    1  ls", "    2  cd /etc",
                                "    3  history"])
        self.assertEqual(self.run_cmd("history 1")[1], ["    4  history 1"])

    def test_clear_and_errors(self):
        """history -c очищает историю; ошибки аргументов."""
        self.run_cmd("ls")
        self.run_cmd("history -c")
        self.assertEqual(self.run_cmd("history")[1], ["    1  history"])
        self.assertIn("numeric", self.run_cmd("history x")[2][0])
        self.assertIn("invalid option", self.run_cmd("history -z")[2][0])
        self.assertIn("too many", self.run_cmd("history 1 2")[2][0])


class TacClearTests(CommandTestCase):
    """Команды tac и clear."""

    def test_tac(self):
        """Строки файлов выводятся в обратном порядке."""
        self.run_cmd("cd ~")
        rows = self.run_cmd("tac notes.txt docs/plan.txt")[1]
        self.assertEqual(rows, ["three", "two", "one", "b", "a"])

    def test_tac_binary(self):
        """Двоичные данные выводятся без падения."""
        self.assertTrue(self.run_cmd("tac /bin.dat")[0])

    def test_tac_errors(self):
        """Нет операнда, нет файла, каталог, неизвестный ключ."""
        self.assertIn("missing file operand", self.run_cmd("tac")[2][0])
        ok, rows, errors = self.run_cmd("tac /none /etc /etc/hostname")
        self.assertFalse(ok)
        self.assertEqual(rows, ["vshell"])
        self.assertIn("failed to open '/none'", errors[0])
        self.assertIn("Is a directory", errors[1])
        self.assertIn("unrecognized option", self.run_cmd("tac -r f")[2][0])

    def test_clear(self):
        """clear очищает экран; лишний аргумент — ошибка."""
        self.run_cmd("ls")
        self.shell.execute("clear")
        self.assertEqual(self.out.records, [])
        self.assertEqual(self.out.cleared, 1)
        self.assertFalse(self.run_cmd("clear now")[0])


if __name__ == "__main__":
    unittest.main()
