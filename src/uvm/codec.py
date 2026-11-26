"""Перевод команд между промежуточным и машинным представлением."""

from uvm.errors import UvmError
from uvm.spec import (
    BYTE_ORDER, OPCODE_MASK, SPEC_BY_OPCODE, Instruction)


def encode(instruction):
    """Переводит команду в байты: поля складываются в одно число,
    которое записывается в порядке little-endian."""
    value = 0
    for field in instruction.spec.fields:
        value |= instruction.values[field.name] << field.low
    return value.to_bytes(instruction.spec.size, BYTE_ORDER)


def assemble(instructions):
    """Переводит список команд в машинный код программы."""
    return b"".join(encode(instruction) for instruction in instructions)


def format_bytes(data):
    """Форматирует байты как в спецификации: 0xE1, 0x53, 0x08."""
    return ", ".join(f"0x{byte:02X}" for byte in data)


def spec_for_opcode(opcode):
    """Возвращает формат команды по коду операции."""
    spec = SPEC_BY_OPCODE.get(opcode)
    if spec is None:
        raise UvmError(f"неизвестный код операции: {opcode}")
    return spec


def decode(data):
    """Переводит байты одной команды обратно в промежуточное представление.

    Длина data должна быть равна размеру команды, код операции берётся
    из младших четырёх бит первого байта.
    """
    spec = spec_for_opcode(data[0] & OPCODE_MASK)
    if len(data) != spec.size:
        raise UvmError(
            f"команда {spec.mnemonic} занимает {spec.size} байт, "
            f"получено {len(data)}")
    value = int.from_bytes(data, BYTE_ORDER)
    values = {field.name: (value >> field.low) & field.mask
              for field in spec.fields}
    return Instruction(spec, values)
