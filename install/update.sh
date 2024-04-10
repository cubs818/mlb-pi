#!/bin/bash


function set_alias() {
  local alias=$1
  local alias_target=$2

  if sudo grep -q "alias $alias=" ~/.bashrc; then
    sed -i "s@alias $alias='.*'@alias $alias=$alias_target@" ~/.bashrc
  else
    echo "alias $alias=$alias_target" >> ~/.bashrc
  fi
}

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