import sys
import os
import signal
import logging
from  threading import Timer
import time
import systemd.daemon

sys.path.append(os.path.abspath('/opt/python-vxi11-server/'))
import vxi11_server as vxi11

#from SimpleTestInst import *
#from SimpleGPIBForward import *
#from ScpiGPIBForward import *
#from Keithley192A import *
#from Keithley192A_Multi import *
#from Philips_PM2534 import *
from Philips_PM2534_Multi import *
#from Keithley487 import *

_logging = logging.getLogger(__name__)


def signal_handler(signal, frame):
    _logging.info('Handling Ctrl+C!')
    instr_server.close()
    sys.exit(0)
        

if __name__ == '__main__':

    
    logging.basicConfig(level=logging.DEBUG)
    _logging = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit')

    _logging.info('starting SRQ test device')

    instr_server = vxi11.InstrumentServer(GPIB_Ethernet_Bridge)

    instr_server.listen()

    # Notifying systemd when the Service is Ready
    systemd.daemon.notify('READY=1')

    # sleep (or do foreground work) while the Instrument threads do their job
    while True:
        time.sleep(1)