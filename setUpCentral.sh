#!/bin/bash
# sudo su
sudo chmod +x ./startUpCentral.sh
sudo chmod +x ./startCentralPi.sh


SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_SCRIPT="$SCRIPT_DIR/startUpCentral.sh"
SERVICE_NAME="autoStartCentral"

if [ ! -f "$TARGET_SCRIPT" ]; then
  echo "❌ Error: Target script not found: $TARGET_SCRIPT"
  exit 1
fi

SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Autostart My Script
After=network.target

[Service]
ExecStart=$TARGET_SCRIPT
WorkingDirectory=$SCRIPT_DIR
StandardOutput=append:/var/log/$SERVICE_NAME.log
StandardError=append:/var/log/$SERVICE_NAME.log
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Reload, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service
sudo systemctl start $SERVICE_NAME.service

echo "✅ Setup complete! $TARGET_SCRIPT will run at every boot."

sudo ./startUpCentral.sh