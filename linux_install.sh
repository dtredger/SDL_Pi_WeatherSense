#!/bin/bash
# Make sure to change permissions of this file to make it executable with
# chmod 777 ./linux_install.sh

sudo apt update
sudo apt install libtool libusb-1.0-0-dev librtlsdr-dev rtl-sdr build-essential autoconf cmake pkg-config git -y

# install switchdoc rtl_433
git clone https://github.com/switchdoclabs/rtl_433.git
cd rtl_433 && mkdir build && cd build && cmake ..
make
sudo make install

# cd ~
# git clone https://github.com/switchdoclabs/SDL_Pi_WeatherRack2.git
#
# cd ~
# git clone https://github.com/switchdoclabs/SDL_Pi_WeatherSense

sudo apt install python3-dev python3-pip libatlas-base-dev -y
sudo pip3 install gpiozero apscheduler RPi.GPIO

# install & set up influxdb
sudo apt install influxdb influxdb-client -y
sudo systemctl unmask influxdb
sudo systemctl enable influxdb
sudo systemctl start influxdb
# systemctl status influxdb.service
# client library for 1.x versions of influxdb
# (raspberry pi defaults to 1.6 as of Jan 2021)
sudo pip3 install influxdb

# install grafana & run
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt install grafana -y
sudo systemctl unmask grafana-server
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
# systemctl status grafana-server.service
# username/pw = admin/admin


sudo apt autoremove
