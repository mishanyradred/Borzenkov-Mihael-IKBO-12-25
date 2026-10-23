@echo off
cd /d "%~dp0\.."
python -m src.main --vfs vfs\files.csv
