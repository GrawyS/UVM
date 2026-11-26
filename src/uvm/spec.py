"""Спецификация УВМ (вариант 6): форматы команд и их внутреннее представление.

Команда хранится как целое число в порядке байт little-endian. Поля
нумеруются от младшего бита: поле A (код операции) занимает биты 0-3.
"""

from dataclasses import dataclass

OPCODE_NAME = "A"
OPCODE_BITS = 4
OPCODE_MASK = (1 << OPCODE_BITS) - 1
REGISTER_BITS = 7
REGISTER_COUNT = 1 << REGISTER_BITS
CONSTANT_BITS = 23
OFFSET_BITS = 12
BYTE_ORDER = "little"


@dataclass(frozen=True)
class Field:
    """Поле команды: имя, номер младшего бита и ширина в битах."""

    name: str
    low: int
    width: int

    @property
    def limit(self):
        """Возвращает число допустимых значений поля."""
        return 1 << self.width

    @property
    def mask(self):
        """Возвращает маску из width единичных битов."""
        return self.limit - 1


@dataclass(frozen=True)
class Spec:
    """Формат команды: мнемоника, код операции, размер и список полей."""

    mnemonic: str
    opcode: int
    size: int
    fields: tuple


OPCODE_FIELD = Field(OPCODE_NAME, 0, OPCODE_BITS)

LOAD = Spec("load", 1, 5, (
    OPCODE_FIELD,
    Field("B", 4, REGISTER_BITS),
    Field("C", 11, CONSTANT_BITS),
))
READ = Spec("read", 13, 3, (
    OPCODE_FIELD,
    Field("B", 4, REGISTER_BITS),
    Field("C", 11, REGISTER_BITS),
))
WRITE = Spec("write", 0, 3, (
    OPCODE_FIELD,
    Field("B", 4, REGISTER_BITS),
    Field("C", 11, REGISTER_BITS),
))
SQRT = Spec("sqrt", 12, 6, (
    OPCODE_FIELD,
    Field("B", 4, OFFSET_BITS),
    Field("C", 16, REGISTER_BITS),
    Field("D", 23, REGISTER_BITS),
    Field("E", 30, OFFSET_BITS),
))

SPECS = (LOAD, READ, WRITE, SQRT)
SPEC_BY_NAME = {spec.mnemonic: spec for spec in SPECS}
SPEC_BY_OPCODE = {spec.opcode: spec for spec in SPECS}


@dataclass(frozen=True)
class Instruction:
    """Команда в промежуточном представлении: формат и значения полей."""

    spec: Spec
    values: dict

    def describe(self):
        """Возвращает поля и значения в виде 'A=1, B=62, C=266'."""
        return ", ".join(
            f"{field.name}={self.values[field.name]}"
            for field in self.spec.fields)


def make_instruction(spec, **operands):
    """Создаёт команду по формату и значениям полей B, C, ...

    Код операции (поле A) подставляется автоматически. Если значение
    не помещается в своё поле, возбуждает ValueError.
    """
    values = {OPCODE_NAME: spec.opcode}
    for field in spec.fields[1:]:
        value = operands[field.name]
        if value not in range(field.limit):
            raise ValueError(
                f"поле {field.name}={value} вне диапазона "
                f"0..{field.mask}")
        values[field.name] = value
    return Instruction(spec, values)
