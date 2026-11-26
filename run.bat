@echo off
setlocal
set PYTHONPATH=%~dp0src
if "%1"=="asm" goto asm
if "%1"=="vm" goto vm
echo Usage: run.bat asm ^| vm ARGS 1>&2
exit /b 2
:asm
shift
python -m uvm.assembler %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%
:vm
shift
python -m uvm.interpreter %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%
