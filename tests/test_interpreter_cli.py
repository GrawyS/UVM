"""Тесты этапа 3: командная строка интерпретатора и дамп JSON."""

import json
import unittest

from uvm.assembler import main as asm_main
from uvm.interpreter import (
    EXIT_ERROR, EXIT_OK, main, parse_range)
from helpers import program_path, run_main, workdir, write_text

SOURCE_VALUES = [101, 202, 303, 404, 505]


def assemble_file(folder, name):
    """Ассемблирует пример программы, возвращает путь к .bin."""
    output = folder + "/prog.bin"
    code, _, _ = run_main(asm_main, program_path(name), output)
    assert code == EXIT_OK
    return output


class InterpreterCliTest(unittest.TestCase):
    """Запуск интерпретатора из командной строки."""

    def test_copy_array_dump(self):
        """Программа копирования массива: дамп источника и копии равны."""
        with workdir() as folder:
            binary = assemble_file(folder, "copy_array.asm")
            dump = folder + "/dump.json"
            code, out, _ = run_main(main, binary, dump, "300:305")
            with open(dump, encoding="utf-8") as handle:
                data = json.load(handle)
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(data["memory"], SOURCE_VALUES)
        self.assertEqual((data["start"], data["end"]), (300, 305))
        self.assertIn("Выполнено команд: 35", out)

    def test_source_array_unchanged(self):
        """Исходный массив после копирования остаётся на месте."""
        with workdir() as folder:
            binary = assemble_file(folder, "copy_array.asm")
            dump = folder + "/dump.json"
            run_main(main, binary, dump, "200:205")
            with open(dump, encoding="utf-8") as handle:
                data = json.load(handle)
        self.assertEqual(data["memory"], SOURCE_VALUES)

    def test_missing_program(self):
        """Отсутствующий двоичный файл даёт ошибку и код 1."""
        code, _, err = run_main(main, "/no/prog.bin", "/tmp/d.json", "0:4")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не удалось прочитать", err)

    def test_bad_range_format(self):
        """Диапазон не в формате НАЧАЛО:КОНЕЦ отклоняется argparse."""
        code, _, err = run_main(main, "p.bin", "d.json", "abc")
        self.assertEqual(code, 2)
        self.assertIn("НАЧАЛО:КОНЕЦ", err)

    def test_range_outside_memory(self):
        """Диапазон за пределами памяти даёт ошибку и код 1."""
        with workdir() as folder:
            binary = write_text(folder, "empty.bin", "")
            code, _, err = run_main(
                main, binary, folder + "/d.json", "0:99999")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("вне памяти", err)

    def test_runtime_error_reported(self):
        """Ошибка выполнения (неизвестный код) выводится без трассировки."""
        with workdir() as folder:
            binary = folder + "/bad.bin"
            with open(binary, "wb") as handle:
                handle.write(b"\x0F\x00\x00")
            code, _, err = run_main(main, binary, folder + "/d.json", "0:4")
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("Ошибка:", err)

    def test_parse_range(self):
        """parse_range разбирает НАЧАЛО:КОНЕЦ."""
        self.assertEqual(parse_range("10:20"), (10, 20))


if __name__ == "__main__":
    unittest.main()
