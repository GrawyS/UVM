"""Ассемблер УВМ: интерфейс командной строки (этапы 1-2)."""

import argparse
import sys

from uvm.codec import assemble, encode, format_bytes
from uvm.errors import UvmError
from uvm.parser import parse_program

EXIT_OK = 0
EXIT_ERROR = 1


def build_arg_parser():
    """Создаёт разбор аргументов командной строки ассемблера."""
    parser = argparse.ArgumentParser(
        prog="asm",
        description="Ассемблер учебной виртуальной машины (вариант 6).",
    )
    parser.add_argument(
        "source", help="путь к исходному файлу с текстом программы")
    parser.add_argument(
        "output", help="путь к двоичному файлу-результату")
    parser.add_argument(
        "--test", action="store_true",
        help="режим тестирования: вывести поля и байты каждой команды")
    return parser


def read_source(path):
    """Читает текст программы из файла."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise UvmError(f"не удалось прочитать '{path}': {exc}") from exc


def write_binary(path, data):
    """Записывает машинный код в двоичный файл."""
    try:
        with open(path, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        raise UvmError(f"не удалось записать '{path}': {exc}") from exc


def print_test_report(instructions):
    """Печатает поля и байты каждой команды (режим тестирования)."""
    for instruction in instructions:
        print(instruction.describe())
        print(format_bytes(encode(instruction)))


def main(argv=None):
    """Запускает ассемблер и возвращает код завершения."""
    args = build_arg_parser().parse_args(argv)
    try:
        instructions = parse_program(read_source(args.source))
        write_binary(args.output, assemble(instructions))
    except UvmError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return EXIT_ERROR
    if args.test:
        print_test_report(instructions)
    print(f"Ассемблировано команд: {len(instructions)}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
