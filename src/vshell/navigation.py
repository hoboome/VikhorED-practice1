"""Команды навигации по VFS: ls и cd."""

from .errors import CommandError
from .memfs import FsError
from .modes import mode_string

LS_OPTIONS = "la"
CD_MAX_ARGS = 1
SIZE_WIDTH = 5
HIDDEN = "."
ONE_TARGET = 1
PREVIOUS = "-"
HOME = "~"


def split_options(name, args, allowed):
    """Отделить ключи вида ``-la`` от остальных аргументов."""
    options, operands = set(), []
    for arg in args:
        if arg.startswith("-") and len(arg) > len("-") and not operands:
            for letter in arg[1:]:
                if letter not in allowed:
                    raise CommandError(
                        f"{name}: invalid option -- '{letter}'")
                options.add(letter)
        else:
            operands.append(arg)
    return options, operands


class NavigationCommands:
    """Команды ls и cd."""

    def home(self):
        """Домашний каталог пользователя или корень, если его нет."""
        path = f"/home/{self.user}"
        entry = self.fs.entries.get(path)
        return path if entry and entry.is_dir else "/"

    def expand(self, path):
        """Подставить домашний каталог вместо ``~``."""
        if path == HOME or path.startswith(HOME + "/"):
            return self.home() + path[len(HOME):]
        return path

    def resolve(self, path):
        """Найти путь в VFS относительно текущего каталога."""
        return self.fs.lookup(self.expand(path), self.cwd)

    def describe(self, name, entry, long_format):
        """Строка вывода ls для одного элемента."""
        if not long_format:
            return name
        size = str(entry.size).rjust(SIZE_WIDTH)
        return (f"{mode_string(entry.mode, entry.is_dir)} 1 "
                f"{entry.owner} {entry.group} {size} {name}")

    def list_directory(self, path, options):
        """Строки вывода ls для содержимого каталога."""
        names = self.fs.children(path)
        if "a" in options:
            names = [".", ".."] + names
        else:
            names = [name for name in names if not name.startswith(HIDDEN)]
        if "l" not in options:
            return ["  ".join(names)] if names else []
        rows = []
        for name in names:
            target = self.fs.absolute(name, path)
            rows.append(self.describe(name, self.fs.entries[target], True))
        return rows

    def cmd_ls(self, args):
        """ls [-l] [-a] [путь...] — содержимое каталогов."""
        options, operands = split_options("ls", args, LS_OPTIONS)
        targets = operands or ["."]
        failed = False
        for target in targets:
            try:
                path, entry = self.resolve(target)
            except FsError as problem:
                self.output.error(f"ls: cannot access '{target}': {problem}")
                failed = True
                continue
            if not entry.is_dir:
                self.output.echo(self.describe(target, entry, "l" in options))
                continue
            if len(targets) > ONE_TARGET:
                self.output.echo(f"{target}:")
            for row in self.list_directory(path, options):
                self.output.echo(row)
        return not failed

    def cmd_cd(self, args):
        """cd [путь | ~ | -] — сменить текущий каталог."""
        if len(args) > CD_MAX_ARGS:
            raise CommandError("cd: too many arguments")
        target = args[0] if args else HOME
        if target == PREVIOUS:
            if self.previous is None:
                raise CommandError("cd: OLDPWD not set")
            target = self.previous
            self.output.echo(target)
        try:
            path, entry = self.resolve(target)
        except FsError as problem:
            raise CommandError(f"cd: {target}: {problem}") from problem
        if not entry.is_dir:
            raise CommandError(f"cd: {target}: Not a directory")
        self.previous, self.cwd = self.cwd, path
