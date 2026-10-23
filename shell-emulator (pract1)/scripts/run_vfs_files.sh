#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
python3 -m src.main --vfs vfs/files.csv --script scripts/startup_stage3.txt
