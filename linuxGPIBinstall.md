
# install basics
./installGPIB.sh

# change the default configuration file to use board_type = "gpib_bitbang"
nano /etc/gpib.conf
# set up the linux-gpib devices
gpib_config
# linux-gpib is now set-up and ready to use, example:
 ibterm -d9 -s96


# Copy Startup script
cp /opt/gpibConf.sh

# And make runable
chmod +x /opt/gpibConf.sh

# Copy SystemD file
cp gpibConf.service /etc/systemd/system/gpibConf.service

# Enable script
systemctl enable gpibConf
