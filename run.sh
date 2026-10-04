#!/usr/bin/env bash
# Запуск эмулятора vshell. Все параметры передаются эмулятору.
here="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$here/src" exec python3 -m vshell "$@"
