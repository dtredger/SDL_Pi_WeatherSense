# Grafana-WeatherSense

WeatherSense monitoring of F016TH (indoor) and FT020T (outdoor) sensors. Changes from the existing system:
- Uses Grafana for data display, rather than the existing python dash-app
- Uses InfluxDB for data-storage (rather than MySQL)
- Removed code related to sensors other than F016TH and FT020T, removed non-metric measurements, and other simplifications.

#### Install

run the script `linux_install.sh` to install all dependencies. SwitchdocLabs rtl_433 will be pulled from github, and other dependencies installed, including:
- InfluxDB installed and service created (note that as of Jan 2022 version 1.6 will be installed _not_ v2.x)
- Grafana installed and service created

*rtl_433* will search for configs in these locations:
- rtl_433.conf
- /home/pi/.config/rtl_433/rtl_433.conf
- /usr/local/etc/rtl_433/rtl_433.conf
- /etc/rtl_433/rtl_433.conf

#### Setup

The various services should auto-start on boot. Setup of Grafana dashboards can all be done in browser (default user/pw = admin/admin)
