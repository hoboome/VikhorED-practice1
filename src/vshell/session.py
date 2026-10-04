"""Команды управления сеансом: exit, history, clear, mount."""

from .errors import CommandError

EXIT_MAX_ARGS = 1
HISTORY_MAX_ARGS = 1
HISTORY_CLEAR = "-c"
NUMBER_WIDTH = 5


def parse_count(name, text):
    """Преобразовать аргумент в неотрицательное целое число."""
    if not text.isdigit():
        raise CommandError(f"{name}: {text}: numeric argument required")
    return int(text)


class SessionCommands:
    """Команды, не работающие с файловой системой."""

    def cmd_exit(self, args):
        """exit [код] — завершить работу эмулятора."""
        if len(args) > EXIT_MAX_ARGS:
            raise CommandError("exit: too many arguments")
        code = parse_count("exit", args[0]) if args else 0
        self.running = False
        self.output.shutdown(code)

    def cmd_history(self, args):
        """history [-c] [N] — история введённых команд."""
        if len(args) > HISTORY_MAX_ARGS:
            raise CommandError("history: too many arguments")
        if args and args[0] == HISTORY_CLEAR:
            self.history.clear()
            return
        if args and args[0].startswith("-"):
            raise CommandError(f"history: {args[0]}: invalid option")
        start = 0
        if args:
            start = max(len(self.history) - parse_count("history", args[0]),
                        0)
        for number in range(start, len(self.history)):
            label = str(number + 1).rjust(NUMBER_WIDTH)
            self.output.echo(f"{label}  {self.history[number]}")

    def cmd_clear(self, args):
        """clear — очистить экран."""
        if args:
            raise CommandError(f"clear: invalid argument '{args[0]}'")
        self.output.clear_screen()

    def cmd_mount(self, args):
        """mount — служебная команда: сведения о подключённой VFS."""
        if args:
            raise CommandError("mount: only listing is supported")
        dirs, files, size = self.fs.statistics()
        source = self.fs.source or "memory"
        self.output.echo(
            f"{source} on / type zipfs (in-memory) "
            f"[{self.fs.name}: {dirs} dirs, {files} files, {size} bytes]")
