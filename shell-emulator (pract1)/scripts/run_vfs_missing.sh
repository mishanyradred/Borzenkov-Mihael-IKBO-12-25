#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
python3 -m src.main --vfs vfs/no_such.csv --script scripts/startup_stage3.txt
