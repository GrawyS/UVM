"""Модель УВМ: единая память, регистры и выполнение команд (этапы 3-4)."""

from math import isqrt

from uvm.codec import decode, spec_for_opcode
from uvm.errors import VmError
from uvm.spec import OPCODE_MASK, REGISTER_COUNT

MEMORY_SIZE = 65536
BYTE_LIMIT = 256


class Machine:
    """УВМ: память команд и данных (общая), регистры, счётчик команд.

    Программа загружается в память с адреса 0 по одному байту на ячейку,
    данные размещаются в той же памяти; ячейка данных хранит целое число.
    """

    def __init__(self, memory_size=MEMORY_SIZE):
        """Создаёт машину с нулевой памятью и нулевыми регистрами."""
        self.memory = [0] * memory_size
        self.registers = [0] * REGISTER_COUNT
        self.program_size = 0
        self.counter = 0
        self.executed = 0
        self.handlers = {
            "load": self.op_load,
            "read": self.op_read,
            "write": self.op_write,
            "sqrt": self.op_sqrt,
        }

    def load_program(self, program):
        """Копирует байты программы в начало памяти."""
        if len(program) > len(self.memory):
            raise VmError("программа не помещается в память")
        self.memory[:len(program)] = list(program)
        self.program_size = len(program)
        self.counter = 0

    def read_memory(self, address):
        """Читает ячейку памяти с проверкой адреса."""
        self.check_address(address)
        return self.memory[address]

    def write_memory(self, address, value):
        """Записывает значение в ячейку памяти с проверкой адреса."""
        self.check_address(address)
        self.memory[address] = value

    def check_address(self, address):
        """Проверяет, что адрес лежит внутри памяти."""
        if address not in range(len(self.memory)):
            raise VmError(
                f"адрес {address} вне памяти (0..{len(self.memory) - 1})")

    def code_byte(self, address):
        """Читает ячейку как байт команды."""
        value = self.read_memory(address)
        if value not in range(BYTE_LIMIT):
            raise VmError(
                f"по адресу {address} не байт команды: {value}")
        return value

    def fetch(self):
        """Читает из памяти очередную команду и переводит её в
        промежуточное представление."""
        first = self.code_byte(self.counter)
        spec = spec_for_opcode(first & OPCODE_MASK)
        data = bytes(self.code_byte(self.counter + shift)
                     for shift in range(spec.size))
        return decode(data)

    def step(self):
        """Выполняет одну команду и сдвигает счётчик команд."""
        instruction = self.fetch()
        name = instruction.spec.mnemonic
        handler = self.handlers.get(name)
        if handler is None:
            raise VmError(f"команда {name} не поддерживается")
        handler(instruction.values)
        self.counter += instruction.spec.size
        self.executed += 1

    def run(self):
        """Выполняет программу до конца и возвращает число команд."""
        while self.counter < self.program_size:
            self.step()
        return self.executed

    def dump(self, start, end):
        """Возвращает содержимое памяти в диапазоне [start, end)."""
        if not start < end <= len(self.memory):
            raise VmError(
                f"диапазон {start}:{end} вне памяти (0..{len(self.memory)})")
        return self.memory[start:end]

    def op_load(self, values):
        """Загрузка константы: регистр B получает константу C."""
        self.registers[values["B"]] = values["C"]

    def op_read(self, values):
        """Чтение: регистр B получает память[регистр C]."""
        address = self.registers[values["C"]]
        self.registers[values["B"]] = self.read_memory(address)

    def op_write(self, values):
        """Запись: память[регистр B] получает значение регистра C."""
        address = self.registers[values["B"]]
        self.write_memory(address, self.registers[values["C"]])

    def op_sqrt(self, values):
        """АЛУ: sqrt. Память[регистр C + E] получает целый корень из
        памяти[регистр D + B] (округление вниз)."""
        source = self.registers[values["D"]] + values["B"]
        target = self.registers[values["C"]] + values["E"]
        self.write_memory(target, isqrt(self.read_memory(source)))
