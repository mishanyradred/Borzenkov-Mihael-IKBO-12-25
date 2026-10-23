@echo off
cd /d "%~dp0\.."
python -m src.main --vfs vfs\no_such.csv --script scripts\startup_stage3.txt
