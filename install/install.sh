#!/bin/bash
function set_config() {
  local line=$1

  if sudo grep -q "$line" /boot/firmware/config.txt; then
    sudo sed -i "s@$line'.*'@$line@" /boot/firmware/config.txt
  else
    sudo sed -i '$a'"$line"'' /boot/firmware/config.txt
  fi
}
function set_alias() {
  local alias=$1
  local alias_target=$2

  if sudo grep -q "alias $alias=" ~/.bashrc; then
    sed -i "s@alias $alias='.*'@alias $alias=$alias_target@" ~/.bashrc
  else
    echo "alias $alias=$alias_target" >> ~/.bashrc
  fi
}

# updates and packages
sudo apt-get update -y
sudo apt-get full-upgrade -y

sudo apt-get -y install python3.11
sudo apt-get -y install python3-pip
sudo apt-get -y install python3.11-venv
sudo apt-get -y install python-is-python3
sudo apt-get -y install  i2c-tools libgpiod-dev python3-libgpiod

# pi configs
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint disable_raspi_config_at_boot 0
set_config "usb_max_current_enable=1"


# smartrack pi module and webserver
python -m venv .venv --system-site-packages
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# python script as services
sudo cp install/mlb.service /etc/systemd/system/mlb.service
sudo systemctl daemon-reload
sudo systemctl enable button.service
sudo systemctl start button.service

