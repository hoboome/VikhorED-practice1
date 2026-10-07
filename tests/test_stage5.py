"""Тесты команды chown."""

import unittest

from vshell.interpreter import Interpreter
from vshell.io import BufferOutput
from vshell.memfs import MemoryFS
from fixture_case import FixtureCase

PASSWD = b"root:x:0:0::/root:/bin/sh\nlena:x:1000:1000::/home/lena:/bin/sh\n"
GROUP = b"root:x:0:\nlena:x:1000:\nstaff:x:50:lena\n"


class ChownTests(FixtureCase):
    """Смена владельца и группы в памяти."""

    def prepare(self):
        """VFS с пользователями root, lena и группой staff."""
        fs = MemoryFS(owner="root")
        fs.add_file("/etc/passwd", PASSWD)
        fs.add_file("/etc/group", GROUP)
        fs.add_file("/srv/app/main.py", b"print(1)\n")
        self.fs = fs
        self.out = BufferOutput()
        self.shell = Interpreter(self.out, fs, user="guest")

    def owner(self, path):
        """Пара (владелец, группа) пути."""
        entry = self.fs.entries[path]
        return entry.owner, entry.group

    def test_forms(self):
        """OWNER, OWNER:GROUP, :GROUP и числовой id."""
        self.shell.execute("chown lena /srv")
        self.assertEqual(self.owner("/srv"), ("lena", "root"))
        self.shell.execute("chown root:staff /srv")
        self.assertEqual(self.owner("/srv"), ("root", "staff"))
        self.shell.execute("chown :lena /srv")
        self.assertEqual(self.owner("/srv"), ("root", "lena"))
        self.shell.execute("chown 1000 /srv")
        self.assertEqual(self.owner("/srv"), ("lena", "lena"))

    def test_current_user_is_known(self):
        """Текущий пользователь допустим, даже если его нет в passwd."""
        self.assertTrue(self.shell.execute("chown guest:guest /srv"))

    def test_recursive_verbose(self):
        """-R меняет всё поддерево, -v сообщает об изменениях."""
        self.shell.execute("chown -Rv lena:staff /srv")
        self.assertEqual(self.owner("/srv/app/main.py"), ("lena", "staff"))
        rows = self.out.lines()
        self.assertEqual(len(rows), 3)
        self.assertIn("from root:root to lena:staff", rows[0])
        self.out.records.clear()
        self.shell.execute("chown -v lena /srv")
        self.assertIn("retained as lena:staff", self.out.lines()[0])

    def test_ls_shows_owner(self):
        """ls -l показывает нового владельца."""
        self.shell.execute("chown lena:staff /srv/app/main.py")
        self.shell.execute("ls -l /srv/app")
        self.assertIn(" lena staff ", self.out.lines()[0])

    def test_errors(self):
        """Ошибки разбора и доступа; права не меняются."""
        cases = {
            "chown": "missing operand",
            "chown lena": "missing operand after 'lena'",
            "chown bob /srv": "invalid user",
            "chown lena:nogroup /srv": "invalid group",
            "chown a:b:c /srv": "invalid spec",
            "chown -q lena /srv": "invalid option",
        }
        for line, message in cases.items():
            self.out.records.clear()
            self.assertFalse(self.shell.execute(line), line)
            self.assertIn(message, self.out.lines("err")[0])
        self.assertEqual(self.owner("/srv"), ("root", "root"))

    def test_partial_failure(self):
        """Ошибка для одного файла не мешает остальным."""
        self.assertFalse(self.shell.execute("chown lena /none /srv"))
        self.assertEqual(self.owner("/srv"), ("lena", "root"))


if __name__ == "__main__":
    unittest.main()
