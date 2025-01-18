# GPIB_Ethernet_Bridge

This starts a VXI11 server that translates the Etherenet input to the GPIB interface.

For the following Devicecs a SCPI translater is avalible

* Keithley 192A, with a multidevice feture where devices can be taked to by using ":CHx"
* Philips_PM2534, with a multidevice feture where devices can be taked to by using ":CHx"

This is based on the usage of the [RaspberyPi GPIB Shield ](http://elektronomikon.org/)

It uses the [Python VXI11 Server](https://github.com/coburnw/python-vxi11-server)

And the SystemD file is based on the instruction from [torfsen](https://github.com/torfsen/python-systemd-tutorial)
