#!/bin/bash
ntpdate -b -u -s pool.ntp.org
sudo apt-get update
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
sudo apt-get install python-lightblue bluez python-gobject python-dbus bluez-utils python-bluez -y
sudo apt-get install dos2unix -y
sudo pip install Adafruit_BBIO 
cd /opt/scripts/tools/
./update_kernel.sh
reboot
