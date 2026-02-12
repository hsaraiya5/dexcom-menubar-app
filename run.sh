#!/bin/bash

# Dexcom Menubar App Runner

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
else
    echo "Virtual environment not found. Please run:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Load environment variables if .env exists
if [ -f "$DIR/.env" ]; then
    export $(cat "$DIR/.env" | grep -v '^#' | xargs)
fi

# Run the app
python -m dexcom_menubar.app
