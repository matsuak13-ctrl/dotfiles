#!/bin/bash
# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate Python virtual environment and run the script
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python3 main.py >> run.log 2>&1
else
    echo "Error: .venv virtual environment not found. Please run ./setup.sh first." >> run.log 2>&1
    exit 1
fi
