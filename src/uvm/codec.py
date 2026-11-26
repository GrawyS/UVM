"""Перевод команд между промежуточным и машинным представлением (этап 2)."""

from uvm.spec import BYTE_ORDER


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
