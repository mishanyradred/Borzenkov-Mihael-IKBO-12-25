@echo off
cd /d "%~dp0\.."
python -m src.main --vfs vfs\deep.csv --script scripts\startup_stage5.txt
