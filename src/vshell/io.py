"""Интерфейс вывода, через который команды общаются с пользователем."""


class Output:
    """Базовый приёмник вывода команд.

    Графическое окно и консоль переопределяют методы ``emit``,
    ``clear_screen`` и ``shutdown``.
    """

    def emit(self, text, style):
        """Показать текст ``text`` в стиле ``style``."""
        raise NotImplementedError

    def echo(self, text):
        """Обычный вывод команды."""
        self.emit(text, "out")

    def error(self, text):
        """Сообщение об ошибке."""
        self.emit(text, "err")

    def note(self, text):
        """Служебное сообщение эмулятора."""
        self.emit(text, "note")

    def clear_screen(self):
        """Очистить экран (по умолчанию ничего не делает)."""

    def shutdown(self, code):
        """Завершить работу с кодом ``code``."""
        raise NotImplementedError


class BufferOutput(Output):
    """Приёмник, сохраняющий весь вывод в список (для тестов)."""

    def __init__(self):
        """Создать пустой буфер."""
        self.records = []
        self.exit_code = None
        self.cleared = 0

    def emit(self, text, style):
        """Запомнить пару (стиль, текст)."""
        self.records.append((style, text))

    def clear_screen(self):
        """Очистить буфер, как очищается экран."""
        self.records.clear()
        self.cleared += 1

    def shutdown(self, code):
        """Запомнить код завершения."""
        self.exit_code = code

    def lines(self, style="out"):
        """Вернуть тексты записей заданного стиля."""
        return [text for kind, text in self.records if kind == style]
