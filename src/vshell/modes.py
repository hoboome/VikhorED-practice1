"""Отображение прав доступа в формате ``ls -l``."""

FLAGS = "rwxrwxrwx"
BIT_COUNT = len(FLAGS)


def mode_string(mode, is_dir):
    """Преобразовать права в строку вида ``drwxr-xr-x``."""
    kind = "d" if is_dir else "-"
    chars = [
        flag if mode & (1 << (BIT_COUNT - 1 - position)) else "-"
        for position, flag in enumerate(FLAGS)
    ]
    return kind + "".join(chars)
