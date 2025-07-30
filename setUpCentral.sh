#!/bin/bash
sudo su
cd ~/Documents
git clone https://github.com/kmeng9025/rpicamlab.git
cd ./rpicamlab
git pull
chmod +x ./startCentralPi.sh
./startCentralPi.sh