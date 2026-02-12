#!/bin/bash

# Dexcom Menubar - Credential Setup Script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
else
    echo "Error: Virtual environment not found."
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Run the setup script
python -m dexcom_menubar.setup
