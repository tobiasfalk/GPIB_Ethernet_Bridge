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

_GPIBAddr = 16
_ReadTrys = 10
_SerialNr = "Test"

class GPIB_Handler():
    
    knowmCmdsQuerry = ["U0", "U1", "U2", "U3", "U4", "U5", 
                       "G0", "G1", "G2", "G3", "G4", "G5", 
                       ]
    knowmCmdsWrite = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", 
                      "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", 
                      "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", 
                      "Z0", "Z1", 
                      "P1", "P2", "P3", 
                      "T1", "T2", "T3", "T4", "T5", "T6", "T7", 
                      "K0", "K1", 
                      "A0", "A0", 
                      "W", 
                      # "M0", "M1", "M2", "M4", "M8", "M16", "M32", # SRQ Not implemented
                      "Q", 
                      "B0", "B1", 
                      "V", 
                      "L1", 
                      "J", 
                      "Y", 
                      "H", 
                      "D", 
                      ]
    
    def __init__(self, gpibAddr = _GPIBAddr, serialNr_in = _SerialNr, resMan = pyvisa.ResourceManager()) -> None:
        self.rm = resMan
        self.inst = self.rm.open_resource("GPIB0::" + str(gpibAddr) + "::INSTR")
        self.serialNr = serialNr_in
        pass
        
    def readGPIB(self):
        respons = ""
        for i in range(_ReadTrys):
            try:
                respons = self.inst.read()
                break
            except:
                time.sleep(.001)
                pass
        return respons    
    
    def handleCommand(self, cmd):
        respons = ""
        if cmd.startswith(tuple(self.knowmCmdsQuerry)) and (cmd.endswith("X?") or cmd.endswith("X")):
            self.inst.write(cmd)
            respons = self.readGPIB()
        elif cmd.startswith(tuple(self.knowmCmdsWrite)) and cmd.endswith("X"):
            self.inst.write(cmd)
            respons = ""
        else:
            respons = self.scpiTranslate(cmd)
        return respons
    
    def scpiTranslate(self, cmd):
        cmd = cmd.upper()
        respons = ""
        
        if cmd[0] == ":":
            cmd = cmd[1:]
        
        if cmd == "*IDN?":
            respons = self.scpiIDN(cmd)
        elif cmd.startswith("FUNC"):
            respons = self.scpiFUNC(cmd)
        elif cmd.startswith("RANGE"):
            respons = self.scpiRANGE(cmd)
        elif cmd.startswith("RATE"):
            respons = self.scpiRATE(cmd)
        elif cmd.startswith("ZERO"):
            respons = self.scpiZERO(cmd)
        elif cmd.startswith("FILTER"):
            respons = self.scpiFILTER(cmd)
        elif cmd.startswith("MULTIPLEX"):
            respons = self.scpiMULTIPLEX(cmd)
        elif cmd.startswith("DELAY"):
            respons = self.scpiDELAY(cmd)
        elif cmd.startswith("CAL"):
            respons = self.scpiCAL(cmd)
        elif cmd.startswith("DISP"):
            respons = self.scpiDISP(cmd)
                    
                    
        return respons
    
    def scpiIDN(self, cmd):
        respons = ""
        self.inst.write("U0X")
        res = self.readGPIB()
        
        if res.startswith("195A"):
            respons = "Keithley 195A Sn.: " + self.serialNr
        elif res.startswith("195"):
            respons = "Keithley 195 Sn.: " + self.serialNr
        else:
            respons = "Unknown, set Sn.: " + self.serialNr
            
        return respons
        
    def scpiFUNC(self, cmd):
        respons = ""
        
        if cmd == ":FUNC?":
            self.inst.write("G0X")
            res = ""
            res = self.readGPIB()
            if res.startswith(tuple(["N", "O", "Z"])):
                respons = res[1] + res[2] + res[3]
            elif res.startswith("DEG"):
                respons = "DEG" + res[3]
            
        else:
            cmd = cmd.replace(":FUNC ", "")
            if cmd == "DCV":
                self.inst.write("F0X")
            elif cmd == "ACV":
                self.inst.write("F1X")
            elif cmd == "OHM":
                self.inst.write("F2X")
            elif cmd == "DCA":
                self.inst.write("F3X")
            elif cmd == "ACA":
                self.inst.write("F4X")
            elif cmd == "DEGF":
                self.inst.write("F5X")
            elif cmd == "DEGC":
                self.inst.write("F6X")
                    
        return respons
        
    def scpiRANGE(self, cmd):
        respons = ""
        cmd = cmd.replace(":RANGE", "")
        
        rangeID = ""
        
        if cmd.endswith("?"):
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            if res.startswith("195A"):
                res = res.replace("195A ", "")
            elif res.startswith("195"):
                res = res.replace("195 ", "")
            rangeID = res[2]
            
        _logging.debug("!!!!!!!!!!!!!! RANGE ID %s",rangeID)
        
        if cmd.startswith(":DCV"):
            if cmd.endswith("?"):
                match rangeID:
                    case "0":
                        respons = "Auto"
                    case "1":
                        respons = "20mV"
                    case "2":
                        respons = "200mV"
                    case "3":
                        respons = "2V"
                    case "4":
                        respons = "20V"
                    case "5":
                        respons = "200V"
                    case "6":
                        respons = "1000V"
                    case "7":
                        respons = "1000V"
            else:
                cmd = cmd.replace(":DCV ", "")
                match cmd:
                    case "AUTO":
                        self.inst.write("R0X")
                    case "20MV":
                        self.inst.write("R1X")
                    case "200MV":
                        self.inst.write("R2X")
                    case "2V":
                        self.inst.write("R3X")
                    case "20V":
                        self.inst.write("R4X")
                    case "200V":
                        self.inst.write("R5X")
                    case "1000V":
                        self.inst.write("R6X")
        elif cmd.startswith(":ACV"):
            if cmd.endswith("?"):
                match rangeID:
                    case "0":
                        respons = "Auto"
                    case "1":
                        respons = "20mV"
                    case "2":
                        respons = "200mV"
                    case "3":
                        respons = "2V"
                    case "4":
                        respons = "20V"
                    case "5":
                        respons = "200V"
                    case "6":
                        respons = "700V"
                    case "7":
                        respons = "700V"
            else:
                cmd = cmd.replace(":ACV ", "")
                match cmd:
                    case "AUTO":
                        self.inst.write("R0X")
                    case "20MV":
                        self.inst.write("R1X")
                    case "200MV":
                        self.inst.write("R2X")
                    case "2V":
                        self.inst.write("R3X")
                    case "20V":
                        self.inst.write("R4X")
                    case "200V":
                        self.inst.write("R5X")
                    case "700V":
                        self.inst.write("R6X")
        elif cmd.startswith(":DCA"):
            if cmd.endswith("?"):
                match rangeID:
                    case "0":
                        respons = "Auto"
                    case "1":
                        respons = "20uA"
                    case "2":
                        respons = "200uA"
                    case "3":
                        respons = "2mA"
                    case "4":
                        respons = "20mA"
                    case "5":
                        respons = "200mA"
                    case "6":
                        respons = "2A"
                    case "7":
                        respons = "2A"
            else:
                cmd = cmd.replace(":DCA ", "")
                match cmd:
                    case "AUTO":
                        self.inst.write("R0X")
                    case "20uA":
                        self.inst.write("R1X")
                    case "200uA":
                        self.inst.write("R2X")
                    case "2mA":
                        self.inst.write("R3X")
                    case "20mA":
                        self.inst.write("R4X")
                    case "200mA":
                        self.inst.write("R5X")
                    case "2A":
                        self.inst.write("R6X")
        elif cmd.startswith(":ACA"):
            if cmd.endswith("?"):
                match rangeID:
                    case "0":
                        respons = "Auto"
                    case "1":
                        respons = "20uA"
                    case "2":
                        respons = "200uA"
                    case "3":
                        respons = "2mA"
                    case "4":
                        respons = "20mA"
                    case "5":
                        respons = "200mA"
                    case "6":
                        respons = "2A"
                    case "7":
                        respons = "2A"
            else:
                cmd = cmd.replace(":ACA ", "")
                match cmd:
                    case "AUTO":
                        self.inst.write("R0X")
                    case "200uA":
                        self.inst.write("R2X")
                    case "2mA":
                        self.inst.write("R3X")
                    case "20mA":
                        self.inst.write("R4X")
                    case "200mA":
                        self.inst.write("R5X")
                    case "2A":
                        self.inst.write("R6X")
        elif cmd.startswith(":OHM"):
            if cmd.endswith("?"):
                match rangeID:
                    case "0":
                        respons = "Auto"
                    case "1":
                        respons = "20Ohm"
                    case "2":
                        respons = "200Ohm"
                    case "3":
                        respons = "2kOhm"
                    case "4":
                        respons = "20kOhm"
                    case "5":
                        respons = "200kOhm"
                    case "6":
                        respons = "2MegOhm"
                    case "7":
                        respons = "20MegOhm"
            else:
                cmd = cmd.replace(":OHM ", "")
                match cmd:
                    case "AUTO":
                        self.inst.write("R0X")
                    case "20OHM":
                        self.inst.write("R1X")
                    case "200OHM":
                        self.inst.write("R2X")
                    case "2KOHM":
                        self.inst.write("R3X")
                    case "20KOHM":
                        self.inst.write("R4X")
                    case "200KOHM":
                        self.inst.write("R5X")
                    case "2MEGOHM":
                        self.inst.write("R6X")
                    case "20MEGOHM":
                        self.inst.write("R7X")
        elif cmd.startswith(":DEG"):
            cmd = cmd.replace(":DEG ", "")
            if cmd.endswith("?"):
                if rangeID == "0":
                    pass
                elif rangeID == "1":
                    respons = "<230°C"
                elif rangeID  in ["2", "3", "4", "5", "6", "7"]:
                    respons = ">230°C"
            
            if cmd == "LOW":
                self.inst.write("R1X")
            elif cmd == "HIGH":
                self.inst.write("R2X")
            pass
        return respons
    
    def scpiRATE(self, cmd):
        respons = ""
        
        if cmd == ":RATE?":
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            if res.startswith("195A"):
                res = res.replace("195A ", "")
            elif res.startswith("195"):
                res = res.replace("195 ", "")
            rangeID = res[6]
            
            match rangeID:
                case "0":
                    respons = "3.33ms"
                case "1":
                    respons = "PLC1"
                case "2":
                    respons = "PLC2"
                case "3":
                    respons = "PLC4"
                case "4":
                    respons = "PLC8"
                case "5":
                    respons = "PLC16"
                case "6":
                    respons = "100ms1"
                case "7":
                    respons = "100ms2"
                case "8":
                    respons = "100ms4"
                case "9":
                    respons = "100ms8"
            
            
            
        else:
            cmd = cmd.replace(":RATE ", "")
            if cmd == "3.33MS":
                self.inst.write("S0X")
            elif cmd == "PLC1":
                self.inst.write("S1X")
            elif cmd == "PLC2":
                self.inst.write("S2X")
            elif cmd == "PLC4":
                self.inst.write("S3X")
            elif cmd == "PLC8":
                self.inst.write("S4X")
            elif cmd == "PLC16":
                self.inst.write("S5X")
            elif cmd == "100MS1":
                self.inst.write("S6X")
            elif cmd == "100MS2":
                self.inst.write("S7X")
            elif cmd == "100MS4":
                self.inst.write("S8X")
            elif cmd == "100MS8":
                self.inst.write("S9X")
                    
        return respons
    
    def scpiZERO(self, cmd):
        respons = ""
        
        if cmd == ":ZERO?":
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            if res.startswith("195A"):
                res = res.replace("195A ", "")
            elif res.startswith("195"):
                res = res.replace("195 ", "")
            rangeID = res[8]
            
            match rangeID:
                case "0":
                    respons = "DISABLED"
                case "1":
                    respons = "ENABLED"
            
        else:
            cmd = cmd.replace(":ZERO ", "")
            if cmd == "DIS" or cmd == "DISABLED":
                self.inst.write("Z0X")
            elif cmd == "ENA" or cmd == "ENABLED":
                self.inst.write("Z1X")
                    
        return respons
    
    def scpiFILTER(self, cmd):
        respons = ""
        
        if cmd == ":FILTER?":
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            if res.startswith("195A"):
                res = res.replace("195A ", "")
            elif res.startswith("195"):
                res = res.replace("195 ", "")
            rangeID = res[15]
            
            match rangeID:
                case "0":
                    respons = "DISABLED"
                case "1":
                    respons = "64RSA"
                case "2":
                    respons = "32RSA"
                case "3":
                    respons = "8RSA"
            
        else:
            cmd = cmd.replace(":FILTER ", "")
            if cmd == "DIS" or cmd == "DISABLED":
                self.inst.write("P0X")
            elif cmd == "64RSA":
                self.inst.write("P1X")
            elif cmd == "32RSA":
                self.inst.write("P2X")
            elif cmd == "8RSA":
                self.inst.write("P3X")
                    
        return respons
    
    def scpiMULTIPLEX(self, cmd):
        respons = ""
        
        if cmd == ":MULTIPLEX?":
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            if res.startswith("195A"):
                res = res.replace("195A ", "")
            elif res.startswith("195"):
                res = res.replace("195 ", "")
            rangeID = res[11]
            
            match rangeID:
                case "0":
                    respons = "ENABLED"
                case "1":
                    respons = "DISABLED"
            
        else:
            cmd = cmd.replace(":MULTIPLEX ", "")
            if cmd == "DIS" or cmd == "DISABLED":
                self.inst.write("A1X")
            elif cmd == "ENA" or cmd == "ENABLED":
                self.inst.write("A0X")
                    
        return respons
    
    def scpiDELAY(self, cmd):
        respons = ""
        
        # Reading Delay not feasable since pyVisa or LinuxGPIB muches the data
        
        if cmd == ":DELAY?":
            pass
            #self.inst.write("U0X")
            #res = ""
            #res = self.readGPIB_raw()
            #resDec = res.decode("ASCII")
            #print(res)
            #print(resDec)
            #if resDec.startswith("195A"):
            #    rangeID = [res[14], res[15]]
            #elif resDec.startswith("195"):
            #    rangeID = [res[13], res[14]]
            #print(rangeID)
            #print("{:08b}".format(rangeID[0]) + " ; " + "{:08b}".format(rangeID[1]))
          
            #binary_list = []
            #binary_list.append(bin(ord(res[9]))[2:].zfill(8))
            #binary_list.append(bin(ord(res[10]))[2:].zfill(8))
          
            #respons = str(binary_list) + " :: " + rangeID
          
            
        else:
            cmd = cmd.replace(":DELAY ", "")
            self.inst.write("W"+ cmd + "X")
                    
        return respons
    
    def scpiCAL(self, cmd):
        respons = ""
        
        if cmd == ":CAL?":
            self.inst.write("U5X")
            respons = self.readGPIB()
            
        else:
            cmd = cmd.replace(":CAL ", "")
            self.inst.write("V"+ cmd + "X")
            self.inst.write("G0X")
            respons = self.readGPIB()
            self.inst.write("G0X")
            respons = respons + ";" + self.readGPIB()
                    
        return respons
    
    def scpiDISP(self, cmd):
        respons = ""
            
        if cmd == ":DISP:CLEAR":
            self.inst.write("DX")
        else:
            cmd = cmd.replace(":DISP ", "")
            self.inst.write("D"+ cmd + "X")
                    
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
        cmdList = cmd.split(";")
        
        for cmdVal in cmdList:
            self._addResponse(_gpibHandler.handleCommand(cmdVal))
        return error


    # def signal_srq(self):
    #     _logging.info("SRQ startet for instrument %s",self.name())
    #     super().signal_srq()