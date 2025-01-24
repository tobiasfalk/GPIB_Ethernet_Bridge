import sys
import os
import signal
import logging
from  threading import Timer
import time
import pyvisa

sys.path.append(os.path.abspath('../python-vxi11-server/'))
import vxi11_server as vxi11

_logging = logging.getLogger(__name__)

_GPIBAddr = [10, 11]
_SerialNr = ["Test_A", "Test_B"]


from Philips_PM2534 import GPIB_Handler

def create_GPIB_Handler():
    if not '_gpibHandler' in locals():
        global _gpibHandlers
        global _resMan
        _resMan = pyvisa.ResourceManager()
        _gpibHandlers = []
        for n in range(len(_GPIBAddr)):
            _gpibHandlers.append(GPIB_Handler(_GPIBAddr[n], _SerialNr[n], _resMan))
                                        
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
        cmdList = cmd.split(";")
        
        for cmdVal in cmdList:
            cmdVal = cmdVal.upper()
            if cmdVal == "*IDN?":
                respons = self.scpiIDN(cmdVal)
                self._addResponse(respons)
                
            elif cmdVal == ":CH?" or cmdVal == ":CHANNEL?":
                respons = self.scpiIDN(cmdVal)
                self._addResponse(respons)
                # respons = "Philips "
                for n in range(len(_GPIBAddr)):
                    # res = _gpibHandlers[n].handleCommand("ID?")
                    # respons = respons + ", " + res.strip() + " " + _SerialNr[n]
                    _gpibHandlers[n].handleCommand("DSP OFF")
                    _gpibHandlers[n].handleCommand("TXT CH_" + str(n))
                    
                time.sleep(10)
                    
                for n in range(len(_GPIBAddr)):
                    _gpibHandlers[n].handleCommand("DX")
                    _gpibHandlers[n].handleCommand("DSP ON")
                    
                
            elif not (cmdVal.startswith(":CH") or cmdVal.startswith(":CHANNEL")):
                self._addResponse(_gpibHandlers[0].handleCommand(cmdVal))
            elif cmdVal.startswith(":CH") and not cmdVal.startswith(":CHANNEL"):
                cmdVal = cmdVal.replace(":CH", "")
                channel = cmdVal.split(":")[0]
                cmdVal = cmdVal.replace(channel, "")
                self._addResponse(_gpibHandlers[int(channel)].handleCommand(cmdVal))
            elif cmdVal.startswith(":CHANNEL"):
                cmdVal = cmdVal.replace(":CHANNEL", "")
                channel = cmdVal.split(":")[0]
                cmdVal = cmdVal.replace(channel, "")
                self._addResponse(_gpibHandlers[int(channel)].handleCommand(cmdVal))
        return error
    
    
    
    
    def scpiIDN(self, cmd):
        respons = ""
        idStr = ""
        fwStr = ""
        snStr = ""
        
        for n in range(len(_GPIBAddr)):
            
            if idStr != "":
                idStr = idStr + " & "
                fwStr = fwStr + " & "
                snStr = snStr + " & "
            
            resId = _gpibHandlers[n].handleCommand("ID?").strip()
            splitRes = resId.split("S")
            
            if resId.startswith("PM2534"):
                idStr = idStr + splitRes[0].strip()
                fwStr = fwStr + splitRes[1].strip()
                snStr = snStr + _SerialNr[n].strip()
            else:
                idStr = idStr + "-"
                fwStr = fwStr + "-"
                snStr = snStr + _SerialNr[n]
            
        # <company name>, <model number>, <serial number>, <firmware revision>
        respons = "Philips, " + idStr + ", " + snStr + ", " + fwStr
        return respons


    # def signal_srq(self):
    #     _logging.info("SRQ startet for instrument %s",self.name())
    #     super().signal_srq()