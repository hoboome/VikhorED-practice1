"""Выполнение стартового скрипта эмулятора."""

COMMENT_PREFIX = "#"


def load_lines(path):
    """Прочитать скрипт: список (номер строки, команда) без пустых строк."""
    with open(path, encoding="utf-8") as handle:
        content = handle.read().splitlines()
    result = []
    for number, raw in enumerate(content, start=1):
        line = raw.strip()
        if line and not line.startswith(COMMENT_PREFIX):
            result.append((number, line))
    return result


def run_startup(terminal, path):
    """Выполнить команды скрипта по очереди.

    Ввод и вывод показываются как диалог с пользователем. Строки с
    ошибками пропускаются, выполнение продолжается. Возвращает список
    номеров пропущенных строк.
    """
    try:
        lines = load_lines(path)
    except (OSError, UnicodeError) as problem:
        terminal.error(f"vshell: cannot run script {path}: {problem}")
        return []
    skipped = []
    for number, line in lines:
        if not terminal.shell.running:
            break
        if not terminal.run_line(line):
            skipped.append(number)
            terminal.note(f"(строка {number} скрипта пропущена)")
    if terminal.shell.running:
        terminal.note(f"скрипт {path} выполнен, пропущено строк: "
                      f"{len(skipped)}")
    return skipped
