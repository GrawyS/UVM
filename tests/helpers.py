"""Общие вспомогательные средства для тестов."""

import contextlib
import io
import os
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAMS = os.path.join(ROOT, "programs")

SPEC_FIELDS = (
    "A=1, B=62, C=266",
    "A=13, B=6, C=30",
    "A=0, B=88, C=68",
    "A=12, B=507, C=98, D=23, E=804",
)


def program_path(name):
    """Возвращает путь к примеру программы из папки programs."""
    return os.path.join(PROGRAMS, name)


def read_program(name):
    """Читает текст примера программы из папки programs."""
    with open(program_path(name), encoding="utf-8") as handle:
        return handle.read()


def write_text(folder, name, text):
    """Записывает текстовый файл во временную папку, возвращает путь."""
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


@contextlib.contextmanager
def workdir():
    """Создаёт временную папку и удаляет её после использования."""
    with tempfile.TemporaryDirectory() as folder:
        yield folder


def run_main(main, *args):
    """Запускает main(args) и возвращает (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(args))
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()
