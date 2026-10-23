@echo off
cd /d "%~dp0\.."
python -m src.main --script scripts\no_such_file.txt
