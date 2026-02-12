#!/bin/bash

# Script to install Dexcom Menubar as a macOS Launch Agent
# This will make the app start automatically when you log in

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$HOME/Library/LaunchAgents/com.dexcom.menubar.plist"

echo "=========================================="
echo "Dexcom Menubar - Launch Agent Installer"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Error: Virtual environment not found at $PROJECT_DIR/venv"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Check if already installed
if [ -f "$PLIST_FILE" ]; then
    echo "Launch agent already exists. Unloading existing agent..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Create the plist file
echo "Creating launch agent configuration..."
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dexcom.menubar</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python</string>
        <string>-m</string>
        <string>dexcom_menubar.app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/dexcom-menubar.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/dexcom-menubar.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "✓ Launch agent configuration created at:"
echo "  $PLIST_FILE"
echo ""

# Load the launch agent
echo "Loading launch agent..."
launchctl load "$PLIST_FILE"

echo ""
echo "✓ Launch agent installed successfully!"
echo ""
echo "The Dexcom Menubar app will now:"
echo "  • Start automatically when you log in"
echo "  • Restart automatically if it crashes"
echo "  • Run in the background"
echo ""
echo "Logs are saved to:"
echo "  $HOME/Library/Logs/dexcom-menubar.log"
echo "  $HOME/Library/Logs/dexcom-menubar.error.log"
echo ""
echo "To uninstall, run:"
echo "  ./uninstall-launch-agent.sh"
echo ""
