#!/bin/bash
# sudo su
sudo nmcli device wifi hotspot ssid rpicamlab password rpicamlab ifname wlan0
python centralPi.py