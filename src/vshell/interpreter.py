"""Интерпретатор команд эмулятора."""

import getpass

from .lexer import split_command

HOST = "vshell"
EXIT_MAX_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды с готовым текстом сообщения."""


class Interpreter:
    """Выполняет строки ввода и выводит результат в ``Output``.

    Команда ``name`` реализуется методом ``cmd_name(self, args)``.
    """

    def __init__(self, output, vfs_name="empty", user=None):
        """Связать интерпретатор с приёмником вывода ``output``."""
        self.output = output
        self.vfs_name = vfs_name
        self.user = user or getpass.getuser()
        self.cwd = "/"
        self.running = True

    def prompt(self):
        """Строка приглашения: ``user@vshell:/path$``."""
        return f"{self.user}@{HOST}:{self.cwd}$ "

    def handler(self, name):
        """Найти метод команды по имени или вернуть None."""
        return getattr(self, "cmd_" + name.replace("-", "_"), None)

    def execute(self, line):
        """Выполнить одну строку. Вернуть True при успехе."""
        name, args = split_command(line)
        if name is None:
            return True
        method = self.handler(name)
        if method is None:
            self.output.error(f"{name}: command not found")
            return False
        try:
            method(args)
        except CommandError as problem:
            self.output.error(str(problem))
            return False
        return True

    def stub(self, name, args):
        """Вывод команды-заглушки: имя и список аргументов."""
        self.output.echo(f"[stub] {name} {args}")

    def cmd_ls(self, args):
        """ls — пока заглушка."""
        self.stub("ls", args)

    def cmd_cd(self, args):
        """cd — пока заглушка."""
        self.stub("cd", args)

    def cmd_exit(self, args):
        """exit [код] — завершить работу эмулятора."""
        if len(args) > EXIT_MAX_ARGS:
            raise CommandError("exit: too many arguments")
        code = 0
        if args:
            if not args[0].lstrip("-").isdigit():
                raise CommandError(
                    f"exit: {args[0]}: numeric argument required")
            code = int(args[0])
        self.running = False
        self.output.shutdown(code)
