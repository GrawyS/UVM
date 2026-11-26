#!/bin/sh
case "$1" in
    asm) module=assembler ;;
    vm) module=interpreter ;;
    *) echo "Использование: run.sh asm|vm АРГУМЕНТЫ" >&2; exit 2 ;;
esac
shift
PYTHONPATH="$(dirname "$0")/src" exec python3 -m "uvm.$module" "$@"
