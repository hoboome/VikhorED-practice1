#!/usr/bin/env bash
# Проверка всех параметров командной строки эмулятора (этап 2).
# Пример: ./os_scripts/check_args.sh --console
cd "$(dirname "$0")/.." || exit 1
extra=("$@")

call() {
    printf '\n>>> ./run.sh %s %s\n' "$*" "${extra[*]}"
    ./run.sh "$@" "${extra[@]}" < /dev/null
    printf '<<< код возврата: %s\n' "$?"
}

call --help
call
call -v fixtures/out/deep.zip
call -s examples/stage2.vsh
call --vfs fixtures/out/deep.zip --script examples/stage2.vsh
call -s examples/exit_code.vsh
call -s examples/missing.vsh
call --bad-option
