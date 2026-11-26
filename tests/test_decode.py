"""Тесты этапа 3: перевод машинного кода обратно в команды."""

import unittest

from uvm.codec import assemble, decode, encode, spec_for_opcode
from uvm.spec import OPCODE_MASK
from uvm.errors import UvmError
from uvm.parser import parse_line, parse_program
from helpers import SPEC_BYTES, SPEC_FIELDS, read_program


class DecodeTest(unittest.TestCase):
    """Декодирование совпадает с тестами спецификации."""

    def test_spec_bytes_to_fields(self):
        """Байты из спецификации дают поля из спецификации."""
        decoded = tuple(decode(data).describe() for data in SPEC_BYTES)
        self.assertEqual(decoded, SPEC_FIELDS)

    def test_roundtrip(self):
        """encode и decode взаимно обратны."""
        for text in ("r127 = 8388607", "r0 = 0", "r5 = [r6]", "[r1] = r2",
                     "[r127 + 4095] = sqrt([r126 + 4094])"):
            item = parse_line(text, 1)
            self.assertEqual(decode(encode(item)), item)

    def test_unknown_opcode(self):
        """Код операции, которого нет в спецификации, - ошибка."""
        with self.assertRaisesRegex(UvmError, "неизвестный код"):
            decode(b"\x0F\x00\x00")

    def test_wrong_length(self):
        """Неверная длина команды - ошибка."""
        with self.assertRaisesRegex(UvmError, "занимает"):
            decode(b"\xE1\x53")

    def test_program_roundtrip(self):
        """Программа целиком восстанавливается из машинного кода."""
        program = parse_program(read_program("copy_array.asm"))
        data = assemble(program)
        restored, offset = [], 0
        while offset < len(data):
            size = spec_for_opcode(data[offset] & OPCODE_MASK).size
            restored.append(decode(data[offset:offset + size]))
            offset += size
        self.assertEqual(restored, program)


if __name__ == "__main__":
    unittest.main()
