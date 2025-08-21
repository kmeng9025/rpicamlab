#!/bin/bash
# sudo su
source ./pythonEnv/Scripts/activate
sudo nmcli device wifi hotspot ifname wlan0 ssid rpicamlab password rpicamlab
python centralPi.py