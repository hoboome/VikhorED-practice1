"""Графическое окно эмулятора: терминал в одном текстовом поле."""

import tkinter as tk

from .io import Output

TITLE = "vshell — {vfs}"
SIZE = "900x560"
FONT = ("Menlo", 13)
THEME = {
    "bg": "#300a24",
    "fg": "#eeeeec",
    "prompt": "#8ae234",
    "out": "#eeeeec",
    "err": "#ef2929",
    "note": "#729fcf",
    "cmd": "#fce94f",
}
INPUT_MARK = "input_start"
SHORTCUT_MASK = 0x4 | 0x8


class TerminalWindow(Output):
    """Окно в стиле терминала: ввод набирается прямо после приглашения."""

    def __init__(self, interpreter_factory, vfs_name):
        """Создать окно; интерпретатор создаётся фабрикой от окна."""
        self.root = tk.Tk()
        self.root.title(TITLE.format(vfs=vfs_name))
        self.root.geometry(SIZE)
        self.text = tk.Text(
            self.root, bg=THEME["bg"], fg=THEME["fg"], font=FONT,
            insertbackground=THEME["fg"], wrap=tk.CHAR, borderwidth=0,
            padx=8, pady=8, undo=False,
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        for style in ("prompt", "out", "err", "note", "cmd"):
            self.text.tag_configure(style, foreground=THEME[style])
        self.exit_code = 0
        self.alive = True
        self.history_index = None
        self.shell = interpreter_factory(self)
        self._bind_keys()
        self.show_prompt()

    def _bind_keys(self):
        """Назначить обработчики клавиш."""
        self.text.bind("<Return>", self.on_enter)
        self.text.bind("<BackSpace>", self.on_backspace)
        self.text.bind("<Key>", self.on_key)
        self.text.bind("<Up>", lambda event: self.browse(-1))
        self.text.bind("<Down>", lambda event: self.browse(1))
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.shutdown(0))
        self.text.focus_set()

    def emit(self, text, style):
        """Вывести строку перед областью ввода."""
        if self.alive:
            self.text.insert(tk.END, text + "\n", style)
            self.text.see(tk.END)

    def show_prompt(self):
        """Напечатать приглашение и отметить начало ввода."""
        if not self.alive:
            return
        self.text.insert(tk.END, self.shell.prompt(), "prompt")
        self.text.mark_set(INPUT_MARK, tk.END + "-1c")
        self.text.mark_gravity(INPUT_MARK, tk.LEFT)
        self.text.mark_set(tk.INSERT, tk.END)
        self.text.see(tk.END)

    def current_input(self):
        """Текст, набранный после приглашения."""
        return self.text.get(INPUT_MARK, tk.END + "-1c")

    def replace_input(self, value):
        """Заменить набранный текст на ``value``."""
        self.text.delete(INPUT_MARK, tk.END + "-1c")
        self.text.insert(tk.END, value, "cmd")

    def on_key(self, event):
        """Не давать редактировать текст выше строки ввода."""
        if self.text.compare(tk.INSERT, "<", INPUT_MARK):
            self.text.mark_set(tk.INSERT, tk.END)
        if event.state & SHORTCUT_MASK:
            return None
        if event.char and event.char.isprintable():
            self.text.insert(tk.INSERT, event.char, "cmd")
            return "break"
        return None

    def on_backspace(self, _event):
        """Удалять символы только внутри строки ввода."""
        if self.text.compare(tk.INSERT, ">", INPUT_MARK):
            self.text.delete(tk.INSERT + "-1c")
        return "break"

    def on_enter(self, _event):
        """Выполнить введённую строку."""
        line = self.current_input()
        self.text.insert(tk.END, "\n")
        self.history_index = None
        self.run_line(line, echo=False)
        return "break"

    def run_line(self, line, echo=True):
        """Выполнить строку; при ``echo`` сначала показать её как ввод."""
        if echo:
            self.text.insert(tk.END, line + "\n", "cmd")
        ok = self.shell.execute(line)
        self.show_prompt()
        return ok

    def browse(self, step):
        """Листать историю команд стрелками."""
        commands = getattr(self.shell, "history", [])
        if not commands:
            return "break"
        if self.history_index is None:
            self.history_index = len(commands)
        index = self.history_index + step
        self.history_index = min(max(index, 0), len(commands))
        if self.history_index < len(commands):
            self.replace_input(commands[self.history_index])
        else:
            self.replace_input("")
        return "break"

    def clear_screen(self):
        """Очистить окно."""
        self.text.delete("1.0", tk.END)

    def shutdown(self, code):
        """Закрыть окно с кодом завершения ``code``."""
        if self.alive:
            self.alive = False
            self.exit_code = code
            self.root.destroy()

    def mainloop(self):
        """Запустить главный цикл и вернуть код завершения."""
        if self.alive:
            self.root.mainloop()
        return self.exit_code
