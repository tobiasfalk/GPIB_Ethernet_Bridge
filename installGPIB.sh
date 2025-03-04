#! /bin/bash


# install build tools
echo "Install_1"
sudo apt -y install subversion build-essential bison flex automake libtool libopenblas-dev liblapack-dev libopenjp2-7 tmux mc git
sudo apt -y install python3 python3-pip python3-venv nodejs
echo "Install_3"
sudo apt-get -y install python3-smbus
sudo apt-get -y install python3-pyvisa python3-pyvisa-py
echo "Install_5"
sudo apt-get -y install python3-scipy python3-openpyxl
sudo apt-get -y install python3-pandas python3-xlrd
echo "Install_7"
sudo apt-get -y install python3-serial
sudo apt-get -y install python3-usb

echo "Linux_GPIB"
git clone git://git.code.sf.net/p/linux-gpib/git linux-gpib-git
cd linux-gpib-git
git pull
# configure, compile and install the linux-gpib userland
cd linux-gpib-user
./bootstrap
./configure --sysconfdir=/etc
make
make install
# update libraries
ldconfig
# install the header files for your linux kernel
apt install raspberrypi-kernel-headers
# change to linux-gpib-kernel directory, build and install
cd ../linux-gpib-kernel
make
make install

#backup original gpib.conf
sudo cp /etc/gpib.conf /etc/gpib.conf.backup


# update the kernels list of modules and load gpib_bitbang
depmod -a
# upon loading the kernel module, set the parameter sn7516x_used to wether you use the driver-ics or not
modprobe gpib_bitbang sn7516x_used=1