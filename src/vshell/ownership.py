"""Команда chown: смена владельца и группы (только в памяти)."""

from .errors import CommandError
from .memfs import FsError

PASSWD_FILE = "/etc/passwd"
GROUP_FILE = "/etc/group"
FIELD_SEPARATOR = ":"
NAME_FIELD = 0
ID_FIELD = 2
CHOWN_OPTIONS = "Rv"
MIN_OPERANDS = 2


def read_accounts(fs, path):
    """Прочитать имена и числовые id из файла вида /etc/passwd."""
    entry = fs.entries.get(path)
    if entry is None or entry.is_dir:
        return {}
    accounts = {}
    for line in entry.data.decode("utf-8", errors="replace").splitlines():
        fields = line.split(FIELD_SEPARATOR)
        if len(fields) > ID_FIELD and fields[NAME_FIELD]:
            accounts[fields[ID_FIELD]] = fields[NAME_FIELD]
    return accounts


class Accounts:
    """Известные пользователи и группы VFS."""

    def __init__(self, fs, current_user):
        """Собрать пользователей и группы из /etc/passwd и /etc/group."""
        self.users = read_accounts(fs, PASSWD_FILE)
        self.groups = read_accounts(fs, GROUP_FILE)
        for table in (self.users, self.groups):
            table.setdefault("0", "root")
            if current_user not in table.values():
                table[f"user:{current_user}"] = current_user

    @staticmethod
    def find(table, name):
        """Найти имя по имени или числовому id; None, если нет."""
        if name in table.values():
            return name
        return table.get(name) if name.isdigit() else None

    def parse(self, spec):
        """Разобрать ``OWNER[:GROUP]``; вернуть (владелец, группа)."""
        owner, _sep, group = spec.partition(FIELD_SEPARATOR)
        if FIELD_SEPARATOR in group or not (owner or group):
            raise CommandError(f"chown: invalid spec: '{spec}'")
        new_owner = self.find(self.users, owner) if owner else None
        if owner and new_owner is None:
            raise CommandError(f"chown: invalid user: '{spec}'")
        new_group = self.find(self.groups, group) if group else None
        if group and new_group is None:
            raise CommandError(f"chown: invalid group: '{spec}'")
        return new_owner, new_group


def split_chown_args(args):
    """Отделить ключи -R/-v, спецификацию владельца и список файлов."""
    options, rest = set(), list(args)
    while rest and rest[0].startswith("-") and len(rest[0]) > len("-"):
        for letter in rest.pop(0)[1:]:
            if letter not in CHOWN_OPTIONS:
                raise CommandError(f"chown: invalid option -- '{letter}'")
            options.add(letter)
    if not rest:
        raise CommandError("chown: missing operand")
    if len(rest) < MIN_OPERANDS:
        raise CommandError(f"chown: missing operand after '{rest[0]}'")
    return options, rest[0], rest[1:]


class OwnershipCommands:
    """Команда chown."""

    def change_owner(self, path, owner, group, verbose):
        """Изменить владельца одного пути и при -v сообщить об этом."""
        entry = self.fs.entries[path]
        before = f"{entry.owner}:{entry.group}"
        entry.owner = owner or entry.owner
        entry.group = group or entry.group
        after = f"{entry.owner}:{entry.group}"
        if not verbose:
            return
        if before == after:
            self.output.echo(f"ownership of '{path}' retained as {after}")
        else:
            self.output.echo(
                f"changed ownership of '{path}' from {before} to {after}")

    def cmd_chown(self, args):
        """chown [-R] [-v] ВЛАДЕЛЕЦ[:ГРУППА] ФАЙЛ... — сменить владельца."""
        options, spec, targets = split_chown_args(args)
        owner, group = Accounts(self.fs, self.user).parse(spec)
        ok = True
        for target in targets:
            try:
                path, _entry = self.resolve(target)
            except FsError as problem:
                self.output.error(
                    f"chown: cannot access '{target}': {problem}")
                ok = False
                continue
            paths = self.fs.subtree(path) if "R" in options else [path]
            for item in paths:
                self.change_owner(item, owner, group, "v" in options)
        return ok
