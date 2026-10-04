"""Команды для работы с содержимым файлов: tac."""

from .errors import CommandError
from .memfs import FsError

ENCODING = "utf-8"


class TextCommands:
    """Команда tac."""

    def read_text(self, name, target):
        """Прочитать файл VFS как текст; ошибки — через CommandError."""
        try:
            _path, entry = self.resolve(target)
        except FsError as problem:
            raise CommandError(
                f"{name}: failed to open '{target}' for reading: {problem}"
            ) from problem
        if entry.is_dir:
            raise CommandError(f"{name}: {target}: read error: "
                               "Is a directory")
        return entry.data.decode(ENCODING, errors="replace")

    def cmd_tac(self, args):
        """tac ФАЙЛ... — вывести строки файлов в обратном порядке."""
        if not args:
            raise CommandError("tac: missing file operand")
        if args[0].startswith("-"):
            raise CommandError(f"tac: unrecognized option '{args[0]}'")
        ok = True
        for target in args:
            try:
                text = self.read_text("tac", target)
            except CommandError as problem:
                self.output.error(str(problem))
                ok = False
                continue
            for line in reversed(text.splitlines()):
                self.output.echo(line)
        return ok
