#! /bin/bash

apt install python3-systemd
git clone https://github.com/coburnw/python-vxi11-server.git /opt/python-vxi11-server

mkdir /opt/GPIB_Ethernet_Bridge/
cp * /opt/GPIB_Ethernet_Bridge/

cp GPIB_Ethernet_Bridge.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/GPIB_Ethernet_Bridge.service
sudo chmod 644 /etc/systemd/system/GPIB_Ethernet_Bridge.service

systemctl daemon-reload
systemctl enable GPIB_Ethernet_Bridge.service
systemctl stop GPIB_Ethernet_Bridge.service
systemctl start GPIB_Ethernet_Bridge.service
