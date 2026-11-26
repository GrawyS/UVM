"""Тесты этапа 1: разбор языка ассемблера и промежуточное представление."""

import unittest

from uvm.errors import AsmError
from uvm.parser import parse_line, parse_program, to_int
from uvm.spec import SPEC_BY_NAME
from helpers import SPEC_FIELDS, read_program


class SpecVectorsTest(unittest.TestCase):
    """Поля и значения команд совпадают с тестами из спецификации."""

    def test_all_spec_commands(self):
        """Файл spec_tests.asm даёт ровно те поля, что в спецификации."""
        program = parse_program(read_program("spec_tests.asm"))
        self.assertEqual(
            tuple(item.describe() for item in program), SPEC_FIELDS)

    def test_load(self):
        """r62 = 266: A=1, B=62, C=266."""
        item = parse_line("r62 = 266", 1)
        self.assertEqual(item.values, {"A": 1, "B": 62, "C": 266})
        self.assertIs(item.spec, SPEC_BY_NAME["load"])

    def test_read(self):
        """r6 = [r30]: A=13, B=6, C=30."""
        item = parse_line("r6 = [r30]", 1)
        self.assertEqual(item.values, {"A": 13, "B": 6, "C": 30})

    def test_write(self):
        """[r88] = r68: A=0, B=88, C=68."""
        item = parse_line("[r88] = r68", 1)
        self.assertEqual(item.values, {"A": 0, "B": 88, "C": 68})

    def test_sqrt(self):
        """Операнд-источник даёт поля B и D, приёмник - C и E."""
        item = parse_line("[r98 + 804] = sqrt([r23 + 507])", 1)
        self.assertEqual(
            item.values, {"A": 12, "B": 507, "C": 98, "D": 23, "E": 804})


class SyntaxTest(unittest.TestCase):
    """Гибкость записи: числа, пробелы, регистр, комментарии."""

    def test_hex_and_underscore(self):
        """Шестнадцатеричные числа и подчёркивания."""
        self.assertEqual(to_int("0x1F"), 31)
        self.assertEqual(to_int("1_000"), 1000)
        self.assertEqual(parse_line("r1 = 0xFF", 1).values["C"], 255)

    def test_optional_offset(self):
        """Смещение можно не писать: оно равно нулю."""
        item = parse_line("[r5] = sqrt([r6])", 1)
        self.assertEqual((item.values["B"], item.values["E"]), (0, 0))

    def test_spaces_and_case(self):
        """Лишние пробелы и заглавные буквы допустимы."""
        item = parse_line("  [R5+2]=SQRT( [r6 +3] )  ", 1)
        self.assertEqual(
            item.values, {"A": 12, "B": 3, "C": 5, "D": 6, "E": 2})

    def test_comments_and_blank(self):
        """Комментарии # и ; и пустые строки пропускаются."""
        text = "# заголовок\n\nr1 = 5  # хвост\n; ещё\nr2 = 6 ; хвост\n"
        self.assertEqual(len(parse_program(text)), 2)

    def test_empty_program(self):
        """Пустая программа даёт пустой список."""
        self.assertEqual(parse_program(""), [])


class ErrorTest(unittest.TestCase):
    """Сообщения об ошибках содержат номер строки."""

    def assert_error(self, text, line):
        """Проверяет, что программа даёт AsmError в нужной строке."""
        with self.assertRaises(AsmError) as caught:
            parse_program(text)
        self.assertEqual(caught.exception.line, line)

    def test_unknown_statement(self):
        """Неизвестная команда."""
        self.assert_error("r1 = 5\nhello world\n", 2)

    def test_register_out_of_range(self):
        """Регистров только 128 (номера 0..127)."""
        self.assert_error("r128 = 1", 1)

    def test_constant_out_of_range(self):
        """Константа - 23 бита, максимум 8388607."""
        self.assert_error("r1 = 8388608", 1)
        self.assertEqual(parse_line("r1 = 8388607", 1).values["C"], 8388607)

    def test_offset_out_of_range(self):
        """Смещение - 12 бит, максимум 4095."""
        self.assert_error("[r1] = sqrt([r2 + 4096])", 1)

    def test_negative_not_supported(self):
        """Отрицательные числа не поддерживаются."""
        self.assert_error("r1 = -5", 1)

    def test_error_message_has_line(self):
        """В тексте ошибки есть слово «строка» и номер."""
        with self.assertRaisesRegex(AsmError, "строка 3"):
            parse_program("r1 = 1\nr2 = 2\noops\n")


if __name__ == "__main__":
    unittest.main()
