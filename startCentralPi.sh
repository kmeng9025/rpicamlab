#!/bin/bash
# sudo su
sudo nmcli device wifi hotspot ifname wlan0 ssid rpicamlab password rpicamlab
python centralPi.py