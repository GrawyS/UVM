"""Тесты этапа 1: командная строка ассемблера и режим тестирования."""

import unittest

from uvm.assembler import EXIT_ERROR, EXIT_OK, main
from helpers import (
    SPEC_FIELDS, program_path, run_main, workdir, write_text)


class AssemblerCliTest(unittest.TestCase):
    """Запуск ассемблера из командной строки."""

    def test_test_mode_prints_fields(self):
        """В режиме --test выводятся поля и значения как в спецификации."""
        with workdir() as folder:
            output = folder + "/prog.bin"
            code, out, _ = run_main(
                main, program_path("spec_tests.asm"), output, "--test")
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(out.splitlines()[:len(SPEC_FIELDS)],
                         list(SPEC_FIELDS))
        self.assertIn("Разобрано команд: 4", out)

    def test_without_test_mode_no_fields(self):
        """Без --test поля не печатаются."""
        with workdir() as folder:
            code, out, _ = run_main(
                main, program_path("spec_tests.asm"), folder + "/p.bin")
        self.assertEqual(code, EXIT_OK)
        self.assertNotIn("A=1", out)

    def test_missing_source(self):
        """Отсутствующий исходный файл даёт ошибку и код 1."""
        code, _, err = run_main(main, "/no/such.asm", "/tmp/x.bin")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не удалось прочитать", err)

    def test_syntax_error_reported(self):
        """Синтаксическая ошибка сообщается с номером строки."""
        with workdir() as folder:
            source = write_text(folder, "bad.asm", "r1 = 1\nfoo\n")
            code, _, err = run_main(main, source, folder + "/p.bin")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("строка 2", err)

    def test_missing_arguments(self):
        """Без аргументов argparse завершает работу с кодом 2."""
        code, _, err = run_main(main)
        self.assertEqual(code, 2)
        self.assertIn("usage", err)


if __name__ == "__main__":
    unittest.main()
