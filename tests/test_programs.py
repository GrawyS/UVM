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
VECTOR_START = 1000
VECTOR_SIZE = 6
VECTOR_CASES = (
    ("sqrt_vector.asm", [1, 4, 9, 16, 25, 36], [1, 2, 3, 4, 5, 6]),
    ("example_squares.asm", [49, 64, 81, 100, 121, 144],
     [7, 8, 9, 10, 11, 12]),
    ("example_arbitrary.asm", [2, 10, 50, 99, 1000, 8388607],
     [1, 3, 7, 9, 31, 2896]),
    ("example_edges.asm", [0, 1, 3, 4, 65536, 1000000],
     [0, 1, 1, 2, 256, 1000]),
)


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


class SqrtVectorTest(unittest.TestCase):
    """Тестовая задача: sqrt над вектором длины 6 на месте (этап 5)."""

    def run_case(self, name):
        """Возвращает вектор до и после выполнения программы."""
        program = assemble(parse_program(read_program(name)))
        machine = Machine()
        machine.load_program(program)
        end = VECTOR_START + VECTOR_SIZE
        steps = len(parse_program(read_program(name)))
        for _ in range(steps - VECTOR_SIZE):
            machine.step()
        before = machine.dump(VECTOR_START, end)
        machine.run()
        return before, machine.dump(VECTOR_START, end)

    def test_task_and_examples(self):
        """Вектор до sqrt равен исходным данным, после - корням."""
        for name, data, roots in VECTOR_CASES:
            with self.subTest(program=name):
                before, after = self.run_case(name)
                self.assertEqual(before, data)
                self.assertEqual(after, roots)

    def test_result_replaces_source(self):
        """Результат записан в тот же вектор: адреса те же, длина 6."""
        for name, _, roots in VECTOR_CASES:
            with self.subTest(program=name):
                _, after = self.run_case(name)
                self.assertEqual(len(after), VECTOR_SIZE)
                self.assertEqual(after, roots)

    def test_floor_property(self):
        """Для каждого результата r: r*r <= x < (r+1)*(r+1)."""
        for name, data, roots in VECTOR_CASES:
            for value, root in zip(data, roots):
                with self.subTest(program=name, value=value):
                    self.assertLessEqual(root * root, value)
                    self.assertLess(value, (root + 1) * (root + 1))


if __name__ == "__main__":
    unittest.main()
