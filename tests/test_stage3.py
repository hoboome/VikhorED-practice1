"""Тесты виртуальной файловой системы."""

import os
import tempfile
import unittest
import zipfile

from vshell.interpreter import Interpreter
from vshell.io import BufferOutput
from vshell.memfs import FsError, MemoryFS, VfsLoadError, load_zip


class ZipTestCase(unittest.TestCase):
    """Базовый класс: создание архивов во временном каталоге."""

    def setUp(self):
        """Временный каталог для архивов."""
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def archive(self, members, name="test.zip"):
        """Создать архив с заданными элементами и вернуть путь."""
        path = os.path.join(self.folder.name, name)
        with zipfile.ZipFile(path, "w") as handle:
            for member, data in members.items():
                handle.writestr(member, data)
        return path


class LoadTests(ZipTestCase):
    """Загрузка VFS из архива."""

    def test_structure(self):
        """Каталоги создаются явно и неявно."""
        fs = load_zip(self.archive({"a/b/c.txt": "x", "d/": ""}), "lena")
        self.assertEqual(fs.name, "test.zip")
        self.assertEqual(fs.children("/"), ["a", "d"])
        self.assertEqual(fs.lookup("/a/b/c.txt")[1].data, b"x")
        self.assertEqual(fs.lookup("/a/b")[1].owner, "lena")
        self.assertEqual(fs.statistics(), (4, 1, 1))

    def test_base64(self):
        """Содержимое base64:... декодируется."""
        fs = load_zip(self.archive({"bin": "base64:AAH/"}))
        self.assertEqual(fs.lookup("/bin")[1].data, b"\x00\x01\xff")

    def test_archive_untouched(self):
        """Архив не изменяется при загрузке."""
        path = self.archive({"f": "1"})
        with open(path, "rb") as handle:
            before = handle.read()
        load_zip(path).entries.clear()
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_errors(self):
        """Нет файла, не ZIP, плохой base64, выход за корень."""
        bad = os.path.join(self.folder.name, "bad.zip")
        with open(bad, "w", encoding="utf-8") as handle:
            handle.write("nope")
        cases = [
            os.path.join(self.folder.name, "none.zip"),
            bad,
            self.archive({"x": "base64:@@@"}, "b64.zip"),
            self.archive({"../up": "1"}, "up.zip"),
        ]
        for path in cases:
            with self.assertRaises(VfsLoadError, msg=path):
                load_zip(path)


class PathTests(unittest.TestCase):
    """Разрешение путей."""

    def setUp(self):
        """Небольшая VFS."""
        self.fs = MemoryFS()
        self.fs.add_file("/home/lena/a.txt", b"a")

    def test_relative(self):
        """Относительные пути, . и .. ."""
        path, entry = self.fs.lookup("../lena/./a.txt", "/home/lena")
        self.assertEqual(path, "/home/lena/a.txt")
        self.assertFalse(entry.is_dir)
        self.assertEqual(self.fs.lookup("/../..")[0], "/")

    def test_missing_and_not_dir(self):
        """Ошибки: нет пути, файл в середине пути."""
        with self.assertRaisesRegex(FsError, "No such"):
            self.fs.lookup("/home/x")
        with self.assertRaisesRegex(FsError, "Not a directory"):
            self.fs.lookup("/home/lena/a.txt/b")

    def test_mount(self):
        """Служебная команда mount показывает сведения о VFS."""
        out = BufferOutput()
        shell = Interpreter(out, self.fs, user="lena")
        shell.execute("mount")
        self.assertIn("3 dirs, 1 files", out.lines()[0])
        self.assertFalse(shell.execute("mount -a"))


if __name__ == "__main__":
    unittest.main()
