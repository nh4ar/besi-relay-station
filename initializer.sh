#!/bin/bash
ntpdate -b -u -s pool.ntp.org
sudo apt-get update
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
sudo apt-get install python-lightblue bluez python-gobject python-dbus bluez-utils python-bluez -y
sudo apt-get install dos2unix -y
sudo pip install Adafruit_BBIO 
sudo pip install setuptools --upgrade
sudo pip uninstall distribute -y
sudo pip install --upgrade setuptools
sudo pip --no-cache-dir install --upgrade numpy
sudo apt-get install python-matplotlib python-scipy python-sklearn python-simplejson python-eyed3 -y
sudo pip --no-cache-dir install --upgrade hmmlearn pydub eyed3
sudo pip --no-cache-dir install https://pypi.python.org/packages/e4/92/c3d26ceeef8f9f960224a8286114988db2cec6f342ad98a0031285ec364d/pyAudioAnalysis-0.1.3.tar.gz
cd /opt/scripts/tools/
git pull
sudo ./update_kernel.sh
reboot
