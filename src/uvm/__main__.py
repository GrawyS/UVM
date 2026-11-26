"""Подсказка по запуску: пакет состоит из двух программ."""

import sys

USAGE = (
    "Запуск:\n"
    "  python -m uvm.assembler ИСХОДНИК ДВОИЧНЫЙ_ФАЙЛ [--test]\n"
)

if __name__ == "__main__":
    sys.stderr.write(USAGE)
    sys.exit(2)
