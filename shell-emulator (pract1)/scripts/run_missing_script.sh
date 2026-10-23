#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
python3 -m src.main --script scripts/no_such_file.txt
