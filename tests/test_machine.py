"""Тесты этапа 3: память, регистры и выполнение команд."""

import unittest

from uvm.codec import assemble
from uvm.errors import UvmError, VmError
from uvm.machine import Machine
from uvm.parser import parse_program

SMALL_MEMORY = 64


def run_text(text, memory_size=SMALL_MEMORY * 16):
    """Ассемблирует текст, выполняет его и возвращает машину."""
    machine = Machine(memory_size)
    machine.load_program(assemble(parse_program(text)))
    machine.run()
    return machine


class CommandsTest(unittest.TestCase):
    """Действие трёх команд этапа 3."""

    def test_load_constant(self):
        """r62 = 266 кладёт 266 в регистр 62."""
        machine = run_text("r62 = 266")
        self.assertEqual(machine.registers[62], 266)
        self.assertEqual(machine.executed, 1)

    def test_write_and_read(self):
        """Запись в память по адресу из регистра и чтение обратно."""
        machine = run_text(
            "r1 = 500\nr2 = 77\n[r1] = r2\nr3 = [r1]\n")
        self.assertEqual(machine.memory[500], 77)
        self.assertEqual(machine.registers[3], 77)

    def test_read_uses_register_as_address(self):
        """Чтение берёт адрес из регистра C, а не само число C."""
        machine = run_text(
            "r1 = 600\nr2 = 5\n[r1] = r2\nr9 = 600\nr8 = [r9]\n")
        self.assertEqual(machine.registers[8], 5)

    def test_registers_independent(self):
        """Разные регистры не влияют друг на друга."""
        machine = run_text("r1 = 10\nr2 = 20\n")
        self.assertEqual(machine.registers[1:3], [10, 20])
        self.assertEqual(machine.registers[0], 0)

    def test_program_loaded_to_memory(self):
        """Код программы лежит в общей памяти с адреса 0."""
        machine = Machine()
        machine.load_program(b"\xE1\x53\x08\x00\x00")
        self.assertEqual(machine.memory[:5], [0xE1, 0x53, 0x08, 0, 0])
        self.assertEqual(machine.program_size, 5)

    def test_empty_program(self):
        """Пустая программа выполняется за ноль команд."""
        machine = Machine()
        machine.load_program(b"")
        self.assertEqual(machine.run(), 0)


class ErrorsTest(unittest.TestCase):
    """Ошибки выполнения."""

    def test_address_out_of_memory(self):
        """Адрес за пределами памяти - ошибка."""
        with self.assertRaisesRegex(VmError, "вне памяти"):
            run_text("r1 = 100000\nr2 = [r1]\n", SMALL_MEMORY * 16)

    def test_sqrt_not_supported_yet(self):
        """На этапе 3 команда sqrt ещё не выполняется."""
        with self.assertRaisesRegex(VmError, "не поддерживается"):
            run_text("[r1] = sqrt([r2])")

    def test_unknown_opcode_in_memory(self):
        """Неизвестный код операции в памяти - ошибка."""
        machine = Machine()
        machine.load_program(b"\x0F\x00\x00")
        with self.assertRaises(UvmError):
            machine.run()

    def test_program_too_big(self):
        """Программа больше памяти не загружается."""
        machine = Machine(memory_size=4)
        with self.assertRaisesRegex(VmError, "не помещается"):
            machine.load_program(bytes(5))

    def test_code_overwritten_by_data(self):
        """Затёртый данными код нельзя выполнить: значение не байт."""
        machine = Machine()
        machine.load_program(b"\x00\x00\x00")
        machine.memory[0] = 1000
        with self.assertRaisesRegex(VmError, "не байт"):
            machine.run()


class DumpTest(unittest.TestCase):
    """Дамп памяти."""

    def test_dump_range(self):
        """Дамп возвращает ячейки [start, end)."""
        machine = Machine(memory_size=SMALL_MEMORY)
        machine.memory[10:13] = [1, 2, 3]
        self.assertEqual(machine.dump(10, 13), [1, 2, 3])

    def test_dump_bad_range(self):
        """Пустой, перевёрнутый и слишком большой диапазоны отклоняются."""
        machine = Machine(memory_size=SMALL_MEMORY)
        for start, end in ((5, 5), (6, 2), (0, SMALL_MEMORY + 1)):
            with self.assertRaises(VmError):
                machine.dump(start, end)


if __name__ == "__main__":
    unittest.main()
