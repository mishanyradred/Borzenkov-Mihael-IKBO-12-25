@echo off
cd /d "%~dp0\.."
python -m src.main --vfs vfs\files.csv --script scripts\startup_demo.txt
