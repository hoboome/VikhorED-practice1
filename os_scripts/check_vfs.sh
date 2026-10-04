#!/usr/bin/env bash
# Проверка работы эмулятора с разными VFS (этап 3).
# Пример: ./os_scripts/check_vfs.sh --console
cd "$(dirname "$0")/.." || exit 1
extra=("$@")
script="${SCRIPT:-examples/stage3.vsh}"

python3 fixtures/build_fixtures.py || exit 1

call() {
    printf '\n>>> ./run.sh %s %s\n' "$*" "${extra[*]}"
    ./run.sh "$@" "${extra[@]}" < /dev/null
    printf '<<< код возврата: %s\n' "$?"
}

call -s "$script"                                   # без VFS: пустая
call -v fixtures/out/minimal.zip -s "$script"       # минимальная
call -v fixtures/out/several.zip -s "$script"       # несколько файлов
call -v fixtures/out/deep.zip -s "$script"          # 3+ уровня вложенности
call -v fixtures/out/absent.zip -s "$script"        # ошибка: нет файла
call -v fixtures/out/corrupt.zip -s "$script"       # ошибка: не ZIP
