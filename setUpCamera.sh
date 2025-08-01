#!/bin/bash
# sudo su
cd ~/Documents
git clone https://github.com/kmeng9025/rpicamlab.git
sudo echo "country=US
network={
    ssid="rpicamlab"
    psk="rpicamlab"
    key_mgmt=WPA-PSK
}" > /etc/wpa_supplicant/wpa_supplicant.conf
cd ./rpicamlab
git pull
sudo chmod +x ./startCameraPi.sh
sudo ./startCameraPi.sh