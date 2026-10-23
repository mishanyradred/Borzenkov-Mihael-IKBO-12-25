@echo off
cd /d "%~dp0\.."
python -m src.main --vfs vfs\minimal.csv --script scripts\startup_stage3.txt
