"""Виртуальная файловая система в памяти.

Файловая система хранится как словарь «абсолютный путь → запись».
Источник — ZIP-архив, который читается целиком в память и никогда не
распаковывается на диск. Двоичные данные хранятся в архиве как текст
вида ``base64:<данные>`` и декодируются при загрузке.
"""

import base64
import binascii
import io
import os
import posixpath
import zipfile
from dataclasses import dataclass

ROOT = "/"
DIR_MODE = 0o755
FILE_MODE = 0o644
MODE_BITS = 0o777
ZIP_ATTR_SHIFT = 16
BASE64_PREFIX = b"base64:"


class FsError(Exception):
    """Ошибка доступа к пути внутри VFS."""


class VfsLoadError(Exception):
    """VFS не удалось загрузить: нет файла или неверный формат."""


@dataclass
class Entry:
    """Файл или каталог VFS."""

    is_dir: bool
    data: bytes = b""
    owner: str = "root"
    group: str = "root"
    mode: int = FILE_MODE

    @property
    def size(self):
        """Размер содержимого в байтах."""
        return len(self.data)


class MemoryFS:
    """Файловая система «путь → запись» с операциями над путями."""

    def __init__(self, name="empty", source=None, owner="root"):
        """Создать VFS, содержащую только корневой каталог."""
        self.name = name
        self.source = source
        self.owner = owner
        self.entries = {ROOT: self._new_entry(True)}

    def _new_entry(self, is_dir, data=b"", mode=None):
        """Создать запись, принадлежащую владельцу VFS."""
        default = DIR_MODE if is_dir else FILE_MODE
        return Entry(is_dir, data, self.owner, self.owner,
                     default if mode is None else mode)

    @staticmethod
    def absolute(path, cwd=ROOT):
        """Нормализовать путь относительно каталога ``cwd``."""
        result = posixpath.normpath(posixpath.join(cwd, path))
        return ROOT + result.lstrip(ROOT)

    @staticmethod
    def parent_of(path):
        """Родительский каталог абсолютного пути."""
        return posixpath.dirname(path) or ROOT

    def lookup(self, path, cwd=ROOT):
        """Вернуть (абсолютный путь, запись) или возбудить FsError."""
        target = self.absolute(path, cwd)
        if target in self.entries:
            return target, self.entries[target]
        probe = self.parent_of(target)
        while probe != ROOT and probe not in self.entries:
            probe = self.parent_of(probe)
        if not self.entries[probe].is_dir:
            raise FsError("Not a directory")
        raise FsError("No such file or directory")

    def children(self, path):
        """Отсортированные имена содержимого каталога ``path``."""
        return sorted(
            posixpath.basename(item) for item in self.entries
            if item != ROOT and self.parent_of(item) == path
        )

    def subtree(self, path):
        """Все пути внутри ``path`` (включая его) в порядке обхода."""
        prefix = path.rstrip(ROOT) + ROOT
        return sorted(item for item in self.entries
                      if item == path or item.startswith(prefix))

    def make_dirs(self, path):
        """Создать каталог ``path`` вместе с недостающими родителями."""
        if path in self.entries:
            if not self.entries[path].is_dir:
                raise VfsLoadError(f"конфликт имён в архиве: {path}")
            return self.entries[path]
        self.make_dirs(self.parent_of(path))
        self.entries[path] = self._new_entry(True)
        return self.entries[path]

    def add_file(self, path, data, mode=None):
        """Добавить файл, создав родительские каталоги."""
        self.make_dirs(self.parent_of(path))
        self.entries[path] = self._new_entry(False, data, mode)

    def statistics(self):
        """Число каталогов, файлов и общий объём данных."""
        dirs = sum(entry.is_dir for entry in self.entries.values())
        total = sum(entry.size for entry in self.entries.values())
        return dirs, len(self.entries) - dirs, total


def _decode(name, data):
    """Раскодировать содержимое вида ``base64:...``."""
    if not data.startswith(BASE64_PREFIX):
        return data
    try:
        return base64.b64decode(data[len(BASE64_PREFIX):], validate=True)
    except (binascii.Error, ValueError) as problem:
        message = f"повреждённые base64-данные: {name}"
        raise VfsLoadError(message) from problem


def _member_path(info):
    """Абсолютный путь элемента архива с проверкой на выход за корень."""
    parts = [part for part in info.filename.split("/") if part]
    if ".." in parts:
        raise VfsLoadError(f"недопустимый путь в архиве: {info.filename}")
    return ROOT + "/".join(parts)


def _member_mode(info):
    """Права элемента архива или None, если они не записаны."""
    return (info.external_attr >> ZIP_ATTR_SHIFT) & MODE_BITS or None


def _fill(fs, archive):
    """Перенести элементы архива в файловую систему."""
    for info in archive.infolist():
        path = _member_path(info)
        if path == ROOT:
            continue
        mode = _member_mode(info)
        if info.is_dir():
            fs.make_dirs(path).mode = mode or DIR_MODE
        else:
            data = _decode(info.filename, archive.read(info))
            fs.add_file(path, data, mode)


def load_zip(path, owner="root"):
    """Загрузить VFS из ZIP-архива в память."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except FileNotFoundError as problem:
        raise VfsLoadError(f"файл не найден: {path}") from problem
    except OSError as problem:
        raise VfsLoadError(f"ошибка чтения {path}: {problem}") from problem
    fs = MemoryFS(os.path.basename(path), path, owner)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            _fill(fs, archive)
    except zipfile.BadZipFile as problem:
        raise VfsLoadError(f"неверный формат, не ZIP: {path}") from problem
    return fs
