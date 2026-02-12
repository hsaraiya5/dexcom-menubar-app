#!/bin/bash

# Script to uninstall Dexcom Menubar Launch Agent

PLIST_FILE="$HOME/Library/LaunchAgents/com.dexcom.menubar.plist"

echo "=========================================="
echo "Dexcom Menubar - Launch Agent Uninstaller"
echo "=========================================="
echo ""

if [ ! -f "$PLIST_FILE" ]; then
    echo "Launch agent is not installed."
    exit 0
fi

echo "Unloading launch agent..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true

echo "Removing launch agent configuration..."
rm -f "$PLIST_FILE"

echo ""
echo "✓ Launch agent uninstalled successfully!"
echo ""
echo "The app will no longer start automatically on login."
echo "You can still run it manually with: ./run.sh"
echo ""
