import sys
import os
import signal
import logging
from  threading import Timer
import time

_logging = logging.getLogger(__name__)

sys.path.append(os.path.abspath('../python-vxi11-server/'))
import vxi11_server as vxi11

class GPIB_Handler():
    def __init__(self) -> None:
        pass
    
    def handleCommand(self, cmd):
        # commands ordered by usage rate
        if cmd.startswith("*IDN?"):
            respons = "GPIB_Ethernet_Bridge Simple Test Inst"
        # elif cmd.startswith("SRQTIMER"):
        #     t= Timer(10, self.signal_srq )
        #     t.start()
        #     self._addResponse("OK")
        else:
            _logging.debug("unsupported vxi11-cmd %s",cmd)
            respons = "Something Else"
        return respons
    
    
def create_GPIB_Handler():
    if not '_gpibHandler' in locals():
        global _gpibHandler
        _gpibHandler = GPIB_Handler()
                                        
class GPIB_Ethernet_Bridge(vxi11.InstrumentDevice):

    def device_init(self):
        self.response = ""
        create_GPIB_Handler()
        return
    
    def device_write(self, opaque_data, flags, io_timeout):
        "The device_write RPC is used to write data to the specified device"
        error = vxi11.Error.NO_ERROR

        commands= opaque_data.decode("ascii").split(";")
        for cmd in commands:
            error= self._processCommand(cmd.strip())
            if error != vxi11.Error.NO_ERROR:
                break
        return error

    def device_read(self, request_size, term_char, flags, io_timeout): 
        "The device_read RPC is used to read data from the device to the controller"
        error = vxi11.Error.NO_ERROR
        aStr=self.response
        self.response=""
        reason = vxi11.ReadRespReason.END
        # returns opaque_data!
        return error, reason, aStr.encode("ascii","ignore")
    
    def _addResponse(self,aStr):
        self.response+=aStr

    def _processCommand(self, cmd ):
        error = vxi11.Error.NO_ERROR
        self._addResponse(_gpibHandler.handleCommand(cmd))
        return error


    # def signal_srq(self):
    #     _logging.info("SRQ startet for instrument %s",self.name())
    #     super().signal_srq()