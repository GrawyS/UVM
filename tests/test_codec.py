"""Тесты этапа 2: перевод команд в машинный код."""

import unittest

from uvm.codec import assemble, encode, format_bytes
from uvm.parser import parse_line, parse_program
from helpers import SPEC_BYTES, SPEC_BYTES_TEXT, read_program


class EncodeTest(unittest.TestCase):
    """Байты команд совпадают со спецификацией."""

    def test_each_spec_command(self):
        """Каждая команда из спецификации даёт свои байты."""
        program = parse_program(read_program("spec_tests.asm"))
        self.assertEqual(
            tuple(encode(item) for item in program), SPEC_BYTES)

    def test_assemble_concatenates(self):
        """Машинный код программы - конкатенация команд."""
        program = parse_program(read_program("spec_tests.asm"))
        self.assertEqual(assemble(program), b"".join(SPEC_BYTES))

    def test_sizes(self):
        """Размеры: загрузка 5, чтение и запись 3, sqrt 6 байт."""
        sizes = [len(encode(parse_line(text, 1))) for text in (
            "r1 = 1", "r1 = [r2]", "[r1] = r2", "[r1] = sqrt([r2])")]
        self.assertEqual(sizes, [5, 3, 3, 6])

    def test_max_values(self):
        """Максимальные значения полей не выходят за размер команды."""
        item = parse_line("r127 = 8388607", 1)
        self.assertEqual(encode(item), b"\xF1\xFF\xFF\xFF\x03")
        item = parse_line("[r127 + 4095] = sqrt([r127 + 4095])", 1)
        self.assertEqual(len(encode(item)), 6)

    def test_empty_program(self):
        """Пустая программа - пустые байты."""
        self.assertEqual(assemble([]), b"")

    def test_format_bytes(self):
        """Формат вывода байтов как в спецификации."""
        self.assertEqual(format_bytes(SPEC_BYTES[0]), SPEC_BYTES_TEXT[0])
        self.assertEqual(format_bytes(b""), "")


if __name__ == "__main__":
    unittest.main()
