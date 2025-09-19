#!/bin/bash
chmod +x ./startCentralPi.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect current user’s home
USER_HOME="$HOME"

# Use LXDE autostart path
AUTOSTART_DIR="$USER_HOME/.config/lxsession/LXDE"
mkdir -p "$AUTOSTART_DIR"

AUTOSTART_FILE="$AUTOSTART_DIR/autostart"

# Remove any old entry for startCentralPi.sh
sed -i '/startCentralPi.sh/d' "$AUTOSTART_FILE" 2>/dev/null || true

# Add a line to start script in lxterminal from this directory
echo "@lxterminal -e \"bash -c 'cd $SCRIPT_DIR && ./startCentralPi.sh; exec bash'\"" >> "$AUTOSTART_FILE"

echo "✅ Setup complete! A terminal window will open at login and run ./startCentralPi.sh from $SCRIPT_DIR."

# Optionally run it right now
./startCentralPi.sh
