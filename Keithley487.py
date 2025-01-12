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

_GPIBAddr = 1
_ReadTrys = 10
_SerialNr = "Test"

class GPIB_Handler():
    
    knowmCmdsQuerry = ["B0", "B1", "B2", "B3", "B4", # Reading Source
                       "L3", # Default Conditions or Calibration
                       "U0", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", # Status Words
                       ]
    knowmCmdsWrite = ["A0", "A1", "A2" # Display Intensity
                      "C0", "C1", "C2", # Zero Check and Correct
                      "D", # Display
                      "F0", "F1", # V/I Ohms
                      "G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", # Data Format
                      "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "H15", "H16", "H17", # Hit COntroll
                      "J1", "J2", # Self-Test
                      "K0", "K1", "K2", "K3", #EOI and Bus Hold-off
                      "L1", "L2", "L4", "L5", "L6", # Default Conditions or Calibration
                      # "M0", "M1", "M2", "M4", "M8", "M16", "M32", "M128", # SRQ Not implemented
                      "N", # Data Store
                      "O0", "O1", # Source Operate
                      "P0", "P1", "P2", "P3", # Filters
                      "Q", # Interval
                      "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", # Range
                      "S0", "S1", # Integration
                      "T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", # Trigger
                      "V", # Voltage source
                      "W", # Delay
                      "Y0", "Y1", "Y2", "Y3", "Y4", # Terminator
                      "Z0", "Z1", "Z2", "Z3", # Relative
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
        elif cmd.startswith("RANGE"):
            respons = self.scpiRANGE(cmd)
        # elif cmd.startswith("RATE"):
        #     respons = self.scpiRATE(cmd)
        # elif cmd.startswith("ZERO"):
        #     respons = self.scpiZERO(cmd)
        # elif cmd.startswith("FILTER"):
        #     respons = self.scpiFILTER(cmd)
        # elif cmd.startswith("MULTIPLEX"):
        #     respons = self.scpiMULTIPLEX(cmd)
        # elif cmd.startswith("DELAY"):
        #     respons = self.scpiDELAY(cmd)
        # elif cmd.startswith("CAL"):
        #     respons = self.scpiCAL(cmd)
        elif cmd.startswith("DISP"):
            respons = self.scpiDISP(cmd)
                    
                    
        return respons
    
    def scpiIDN(self, cmd):
        respons = ""
        self.inst.write("U2X")
        res = self.readGPIB()
        
        print(res)
        
        if res.startswith("486") or res.startswith("487"):
            respons = "Keithley " + res.strip() + " Sn.: " + self.serialNr
        else:
            respons = "Unknown, set Sn.: " + self.serialNr
            
        return respons
        
    def scpiRANGE(self, cmd):
        respons = ""
        cmd = cmd.replace("RANGE", "")
        
        rangeID = ""
        
        if cmd.endswith("?"):
            self.inst.write("U0X")
            res = ""
            res = self.readGPIB()
            
            res = res[32:35]
            
            match res[2]:
                case "1":
                    respons = "2nA"
                case "2":
                    respons = "20nA"
                case "3":
                    respons = "200nA"
                case "4":
                    respons = "2uA"
                case "5":
                    respons = "20uA"
                case "6":
                    respons = "200uA"
                case "7":
                    respons = "2mA"
                    
            
            
            match res[1]:
                case "0":
                    respons = respons + " Auto Disabled"
                case "1":
                    respons = respons + " Auto Enabled"
        else:
            match cmd:
                case "ENAUTO":
                    self.inst.write("R0X")
                case "2NV":
                    self.inst.write("R1X")
                case "20NV":
                    self.inst.write("R2X")
                case "200NV":
                    self.inst.write("R3X")
                case "2UV":
                    self.inst.write("R4X")
                case "20UV":
                    self.inst.write("R5X")
                case "200UV":
                    self.inst.write("R6X")
                case "2MV":
                    self.inst.write("R7X")
                case "DISAUTO":
                    self.inst.write("R10X")
            pass
        
        return respons
    
    def scpiRATE(self, cmd):
        respons = ""
        
        if cmd == "RATE?":
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
            cmd = cmd.replace("RATE ", "")
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
        
        if cmd == "ZERO?":
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
            cmd = cmd.replace("ZERO ", "")
            if cmd == "DIS" or cmd == "DISABLED":
                self.inst.write("Z0X")
            elif cmd == "ENA" or cmd == "ENABLED":
                self.inst.write("Z1X")
                    
        return respons
    
    def scpiFILTER(self, cmd):
        respons = ""
        
        if cmd == "FILTER?":
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
            cmd = cmd.replace("FILTER ", "")
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
        
        if cmd == "MULTIPLEX?":
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
            cmd = cmd.replace("MULTIPLEX ", "")
            if cmd == "DIS" or cmd == "DISABLED":
                self.inst.write("A1X")
            elif cmd == "ENA" or cmd == "ENABLED":
                self.inst.write("A0X")
                    
        return respons
    
    def scpiDELAY(self, cmd):
        respons = ""
        
        # Reading Delay not feasable since pyVisa or LinuxGPIB muches the data
        
        if cmd == "DELAY?":
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
            cmd = cmd.replace("DELAY ", "")
            self.inst.write("W"+ cmd + "X")
                    
        return respons
    
    def scpiCAL(self, cmd):
        respons = ""
        
        if cmd == "CAL?":
            self.inst.write("U5X")
            respons = self.readGPIB()
            
        else:
            cmd = cmd.replace("CAL ", "")
            self.inst.write("V"+ cmd + "X")
            self.inst.write("G0X")
            respons = self.readGPIB()
            self.inst.write("G0X")
            respons = respons + ";" + self.readGPIB()
                    
        return respons
    
    def scpiDISP(self, cmd):
        respons = ""
        
        if cmd == "DISP:CLEAR":
            self.inst.write("DX")
        else:
            cmd = cmd.replace("DISP ", "")
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