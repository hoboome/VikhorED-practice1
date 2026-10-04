"""Сборка тестовых ZIP-архивов VFS в каталог fixtures/out.

Архивы в репозитории не хранятся: их создаёт этот скрипт.
Запуск: ``python3 fixtures/build_fixtures.py``.
"""

import base64
import pathlib
import sys
import zipfile

OUT_DIR = pathlib.Path(__file__).resolve().parent / "out"
STAMP = (2026, 9, 15, 10, 30, 0)
UNIX_SYSTEM = 3
ATTR_SHIFT = 16
TYPE_DIR = 0o040000
TYPE_FILE = 0o100000


def b64(data):
    """Закодировать двоичные данные в формат ``base64:...``."""
    return b"base64:" + base64.b64encode(data)


PASSWD = (
    "root:x:0:0:root:/root:/bin/sh\n"
    "lena:x:1000:1000:Lena:/home/lena:/bin/sh\n"
    "guest:x:1001:1001:Guest:/home/guest:/bin/sh\n"
    "www:x:33:33:web server:/var/www:/usr/sbin/nologin\n"
)

GROUP = "root:x:0:\nlena:x:1000:\nguest:x:1001:\nwww:x:33:\nstaff:x:50:lena\n"

ARCHIVES = {
    "minimal.zip": {
        "readme.txt": "minimal VFS: one file\n",
    },
    "several.zip": {
        "notes.txt": "first\nsecond\nthird\n",
        "todo.txt": "ls\ncd\nhistory\ntac\n",
        "data.csv": "id;name\n1;alpha\n2;beta\n",
        "logo.bin": b64(bytes(range(32))),
    },
    "deep.zip": {
        "etc/": None,
        "etc/passwd": PASSWD,
        "etc/group": GROUP,
        "etc/hostname": "vshell\n",
        "home/": None,
        "home/lena/": None,
        "home/lena/diary.txt": "monday\ntuesday\nwednesday\nthursday\n",
        "home/lena/study/": None,
        "home/lena/study/config/": None,
        "home/lena/study/config/practice1/": None,
        "home/lena/study/config/practice1/plan.txt":
            "stage 1\nstage 2\nstage 3\nstage 4\nstage 5\n",
        "home/lena/study/config/practice1/icon.bin": b64(b"\x89PNG\r\n"),
        "home/guest/": None,
        "home/guest/hello.txt": "hello from guest\n",
        "var/": None,
        "var/www/": None,
        "var/www/index.html": "<h1>vshell</h1>\n",
        "var/log/": None,
        "var/log/system.log": "boot\nlogin lena\nlogout lena\n",
        "tmp/": None,
    },
}

MODES = {
    "etc/passwd": 0o644,
    "home/guest/": 0o750,
    "var/log/system.log": 0o640,
    "tmp/": 0o777,
}


def member(name):
    """Описание элемента архива с правами UNIX."""
    info = zipfile.ZipInfo(name, STAMP)
    is_dir = name.endswith("/")
    mode = MODES.get(name, 0o755 if is_dir else 0o644)
    kind = TYPE_DIR if is_dir else TYPE_FILE
    info.create_system = UNIX_SYSTEM
    info.external_attr = (kind | mode) << ATTR_SHIFT
    return info


def build(name, content):
    """Записать один архив."""
    target = OUT_DIR / name
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for item, data in content.items():
            archive.writestr(member(item), data or "")
    print(f"built {target.relative_to(OUT_DIR.parent.parent)}")


def main():
    """Собрать все архивы и один повреждённый файл."""
    OUT_DIR.mkdir(exist_ok=True)
    for name, content in ARCHIVES.items():
        build(name, content)
    corrupt = OUT_DIR / "corrupt.zip"
    corrupt.write_text("PK? definitely not a zip\n", encoding="utf-8")
    print(f"built {corrupt.relative_to(OUT_DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
