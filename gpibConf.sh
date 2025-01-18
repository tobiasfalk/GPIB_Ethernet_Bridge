#!/bin/sh -e
# update the kernels list of modules and load gpib_bitbang
depmod -a
# upon loading the kernel module, set the parameter sn7516x_used to wether you use the driver-ics or not
modprobe gpib_bitbang sn7516x_used=1
# set up the linux-gpib devices
gpib_config