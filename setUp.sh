#!/bin/bash
sudo su
containsFive=cat /sys/firmware/devicetree/base/model | grep -a "Raspberry Pi 5"
if [${#containsFive} -gt 0]; then
    sudo su
    cd ~/Documents
    git clone https://github.com/kmeng9025/rpicamlab.git
    cd ./rpicamlab
    git pull
    chmod +x ./startCentralPi.sh
    ./startCentralPi.sh
else
    cd ~/Documents
    git clone https://github.com/kmeng9025/rpicamlab.git
    echo "country=US
    network={
        ssid="rpicamlab"
        psk="rpicamlab"
        key_mgmt=WPA-PSK
    }" > /etc/wpa_supplicant/wpa_supplicant.conf
    cd ./rpicamlab
    git pull
    chmod +x ./startCameraPi.sh
    ./startCameraPi.sh
fi