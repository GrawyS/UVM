"""Исключения ассемблера и интерпретатора УВМ."""


class UvmError(Exception):
    """Базовая ошибка ассемблера и интерпретатора."""


class AsmError(UvmError):
    """Ошибка в тексте программы на языке ассемблера."""

    def __init__(self, line, message):
        """Запоминает номер строки и добавляет его в сообщение."""
        super().__init__(f"строка {line}: {message}")
        self.line = line
