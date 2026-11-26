"""Тесты программ из папки programs: ассемблирование и выполнение."""

import unittest

from uvm.codec import assemble
from uvm.machine import Machine
from uvm.parser import parse_program
from helpers import read_program

COPY_SOURCE = 200
COPY_TARGET = 300
COPY_VALUES = [101, 202, 303, 404, 505]
DEMO_SOURCE = 1000
DEMO_TARGET = 1100
DEMO_VALUES = [144, 2025, 2, 0, 1000000]
DEMO_ROOTS = [12, 45, 1, 0, 1000]


def run_program(name):
    """Ассемблирует программу из папки programs и выполняет её."""
    machine = Machine()
    machine.load_program(assemble(parse_program(read_program(name))))
    machine.run()
    return machine


class ProgramsTest(unittest.TestCase):
    """Результаты выполнения примеров программ."""

    def test_copy_array(self):
        """Массив скопирован, исходный не изменён."""
        machine = run_program("copy_array.asm")
        size = len(COPY_VALUES)
        self.assertEqual(
            machine.dump(COPY_SOURCE, COPY_SOURCE + size), COPY_VALUES)
        self.assertEqual(
            machine.dump(COPY_TARGET, COPY_TARGET + size), COPY_VALUES)

    def test_sqrt_demo(self):
        """Корни вычислены и сохранены в память, исходные данные целы."""
        machine = run_program("sqrt_demo.asm")
        size = len(DEMO_VALUES)
        self.assertEqual(
            machine.dump(DEMO_SOURCE, DEMO_SOURCE + size), DEMO_VALUES)
        self.assertEqual(
            machine.dump(DEMO_TARGET, DEMO_TARGET + size), DEMO_ROOTS)


if __name__ == "__main__":
    unittest.main()
