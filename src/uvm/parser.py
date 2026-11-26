"""Разбор программы на языке ассемблера «алгебраического» вида (этап 1).

Поддерживаются четыре формы команд (r5 - регистр с номером 5)::

    r5 = 266                         загрузка константы
    r6 = [r30]                       чтение из памяти
    [r88] = r68                      запись в память
    [r98 + 804] = sqrt([r23 + 507])  квадратный корень

Комментарий начинается с символа # или ;. Числа можно записывать в
десятичном виде или в шестнадцатеричном (0x1F), допускается подчёркивание.
"""

import re

from uvm.errors import AsmError
from uvm.spec import SPEC_BY_NAME, make_instruction

HEX_PREFIX = "0x"
HEX_BASE = 16
DEC_BASE = 10
COMMENT = re.compile(r"[#;].*$")
NUMBER = r"(0[xX][0-9a-fA-F_]+|\d[\d_]*)"
REGISTER = r"[rR](\d+)"
MEMORY = rf"\[\s*{REGISTER}(?:\s*\+\s*{NUMBER})?\s*\]"

LOAD_RE = re.compile(rf"^{REGISTER}\s*=\s*{NUMBER}$")
READ_RE = re.compile(rf"^{REGISTER}\s*=\s*\[\s*{REGISTER}\s*\]$")
WRITE_RE = re.compile(rf"^\[\s*{REGISTER}\s*\]\s*=\s*{REGISTER}$")
SQRT_RE = re.compile(
    rf"^{MEMORY}\s*=\s*sqrt\(\s*{MEMORY}\s*\)$", re.IGNORECASE)


def to_int(text):
    """Переводит запись числа (десятичную или 0x...) в целое."""
    clean = text.replace("_", "")
    if clean.lower().startswith(HEX_PREFIX):
        return int(clean, HEX_BASE)
    return int(clean, DEC_BASE)


def to_offset(text):
    """Переводит смещение в число; отсутствующее смещение равно нулю."""
    return to_int(text) if text else 0


def build_load(groups):
    """Строит команду загрузки константы: rB = C."""
    register, constant = groups
    return make_instruction(
        SPEC_BY_NAME["load"], B=to_int(register), C=to_int(constant))


def build_read(groups):
    """Строит команду чтения из памяти: rB = [rC]."""
    target, source = groups
    return make_instruction(
        SPEC_BY_NAME["read"], B=to_int(target), C=to_int(source))


def build_write(groups):
    """Строит команду записи в память: [rB] = rC."""
    address, source = groups
    return make_instruction(
        SPEC_BY_NAME["write"], B=to_int(address), C=to_int(source))


def build_sqrt(groups):
    """Строит команду sqrt: [rC + E] = sqrt([rD + B])."""
    target, target_offset, source, source_offset = groups
    return make_instruction(
        SPEC_BY_NAME["sqrt"],
        B=to_offset(source_offset),
        C=to_int(target),
        D=to_int(source),
        E=to_offset(target_offset),
    )


STATEMENTS = (
    (LOAD_RE, build_load),
    (READ_RE, build_read),
    (WRITE_RE, build_write),
    (SQRT_RE, build_sqrt),
)


def parse_line(text, number):
    """Разбирает одну строку; для пустой строки или комментария - None."""
    code = COMMENT.sub("", text).strip()
    if not code:
        return None
    for pattern, builder in STATEMENTS:
        found = pattern.match(code)
        if found:
            try:
                return builder(found.groups())
            except ValueError as exc:
                raise AsmError(number, str(exc)) from exc
    raise AsmError(number, f"не удалось разобрать команду: {code}")


def parse_program(text):
    """Переводит текст программы в список команд (промежуточное
    представление)."""
    parsed = (parse_line(line, number)
              for number, line in enumerate(text.splitlines(), start=1))
    return [instruction for instruction in parsed if instruction]
