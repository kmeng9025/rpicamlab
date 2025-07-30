#!/bin/bash
cd ~/Documents
git clone https://github.com/kmeng9025/rpicamlab.git
cd ./rpicamlab
git pull
containsFive=cat /sys/firmware/devicetree/base/model | grep -a "Raspberry Pi 5"
if [${#containsFive} -gt 0]; then
    sudo chmod +x ./setUpCentral.sh
    sudo ./setUpCentral.sh
else
    sudo chmod +x ./setUpCamera.sh
    sudo ./setUpCamera.sh
fi