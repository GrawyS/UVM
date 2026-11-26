"""Интерпретатор УВМ: интерфейс командной строки (этап 3)."""

import argparse
import json
import re
import sys

from uvm.errors import UvmError
from uvm.machine import Machine

EXIT_OK = 0
EXIT_ERROR = 1
RANGE = re.compile(r"^(\d+):(\d+)$")


def parse_range(text):
    """Разбирает диапазон адресов 'НАЧАЛО:КОНЕЦ' (конец не включается)."""
    found = RANGE.match(text)
    if not found:
        raise argparse.ArgumentTypeError(
            f"диапазон '{text}' должен иметь вид НАЧАЛО:КОНЕЦ, например 0:16")
    return int(found.group(1)), int(found.group(2))


def build_arg_parser():
    """Создаёт разбор аргументов командной строки интерпретатора."""
    parser = argparse.ArgumentParser(
        prog="vm",
        description="Интерпретатор учебной виртуальной машины (вариант 6).",
    )
    parser.add_argument(
        "program", help="путь к двоичному файлу с программой")
    parser.add_argument(
        "dump", help="путь к JSON-файлу для дампа памяти")
    parser.add_argument(
        "memory_range", type=parse_range, metavar="НАЧАЛО:КОНЕЦ",
        help="диапазон адресов памяти для дампа (конец не включается)")
    return parser


def read_program(path):
    """Читает двоичную программу из файла."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        raise UvmError(f"не удалось прочитать '{path}': {exc}") from exc


def write_dump(path, start, cells):
    """Сохраняет дамп памяти в формате JSON."""
    data = {"start": start, "end": start + len(cells), "memory": cells}
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        raise UvmError(f"не удалось записать '{path}': {exc}") from exc


def execute(args):
    """Загружает и выполняет программу, сохраняет дамп памяти."""
    machine = Machine()
    machine.load_program(read_program(args.program))
    executed = machine.run()
    start, end = args.memory_range
    write_dump(args.dump, start, machine.dump(start, end))
    return executed


def main(argv=None):
    """Запускает интерпретатор и возвращает код завершения."""
    args = build_arg_parser().parse_args(argv)
    try:
        executed = execute(args)
    except UvmError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return EXIT_ERROR
    start, end = args.memory_range
    print(f"Выполнено команд: {executed}")
    print(f"Дамп памяти [{start}:{end}) сохранён в {args.dump}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
