#*****************************************************
#OW
# STorM32 Python library to handle serial RC commands
# http://www.olliw.eu/storm32bgc-wiki/Serial_Communication#Serial_Communication_-_RC_Commands
# (c) olliw, www.olliw.eu, GPL3
# version 29. Nov. 2020
#*****************************************************
#
#*****************************************************
# Example usage for CMD_SETANGLES:
# import serial
# from STorM32_lib import *
# ser = serial.Serial("COM1", 115200) 
# cmd = cCMD_SETANGLES(ser)
# cmd.send()
#*****************************************************

import struct


#------------------------------------------------------
# Basic RCCMD Class
#------------------------------------------------------

class cSTorM32RcCmd():

    def __init__(self,ser=None,payload=None,noresponse=False):
        if noresponse:
            self.stx = b'\xF9'
        else:    
            self.stx = b'\xFA'
        self.stx = b'\xF9'
        self.len = b'\x00'
        self.cmd = b'\x01'
        self.payload = b''
        self.crc = b'\x33\x34'
        
        self.datastream = b''
        self.ser = ser
        
        if payload != None:
            self.setPayload(payload)

    def enableResponse(self):
        self.stx = b'\xFA'
        return True

    def disableResponse(self):
        self.stx = b'\xF9'
        return True
        
    def setPayload(self,payload):
        self.payload = payload
        return True
        
    def finalize(self,noresponse=None):
        if noresponse == None:
            self.datastream = self.stx
        elif noresponse == True:
            self.datastream = b'\xF9'
        else:
            self.datastream = b'\xFA'
        self.datastream += self.len + self.cmd + self.payload + self.crc
        return True
        
    def getCmd(self):
        return self.datastream

    def send(self):
        if self.ser == None:
            return False
        if not self.finalize():
            return False
        self.ser.write(self.datastream)
        return True
            

#------------------------------------------------------
# RCCMD  GetVersion  #1 = 0x01
#------------------------------------------------------
# has a response
# outgoing: 5 bytes = 434us @ 115200bps

class cCMD_GETVERSION(cSTorM32RcCmd):

    def __init__(self,ser=None,payload=None,noresponse=False):
        super().__init__(ser,noresponse,payload)
        self.len = b'\x00'
        self.cmd = b'\x01'


#------------------------------------------------------
# RCCMD  GetVersionStr  #2 = 0x02
#------------------------------------------------------
# has a response
# outgoing: 5 bytes = 434us @ 115200bps

class cCMD_GETVERSIONSTR(cSTorM32RcCmd):

    def __init__(self,ser=None,payload=None,noresponse=False):
        super().__init__(ser,noresponse,payload)
        self.len = b'\x00'
        self.cmd = b'\x02'


#------------------------------------------------------
# RCCMD  SetAngles  #17 = 0x11
#------------------------------------------------------
# only outgoing, has no response (except of an ACK)
# outgoing: 19 bytes = 1650us @ 115200bps

class cCMD_SETANGLES (cSTorM32RcCmd):

    def __init__(self,ser=None,pitch_deg=0.0,roll_deg=0.0,yaw_deg=0.0,noresponse=True):
        super().__init__(ser,None,noresponse)
        self.len = b'\x0E'
        self.cmd = b'\x11'
        self.setPayload(pitch_deg,roll_deg,yaw_deg)

    def setPayload(self,pitch_deg,roll_deg,yaw_deg):
        self.pitch_deg = pitch_deg
        self.roll_deg = roll_deg
        self.yaw_deg = yaw_deg
        self.payload = struct.pack("fff", self.pitch_deg, self.roll_deg, self.yaw_deg) + b'\x00\x00'


#------------------------------------------------------
# RCCMD  SendCameraCommand  #27 = 0x1B
#------------------------------------------------------
# only outgoing, has no response (except of an ACK)
# outgoing: 6 - 29 bytes = 521us - 2518us @ 115200bps

class cCMD_SENDCAMERACOMMAND(cSTorM32RcCmd):

    def __init__(self,ser=None,payload=None,noresponse=True):
        super().__init__(ser,payload,noresponse)
        self.cmd = b'\x1B'

    def setPayload(self,payload):
        plen = len(payload)
        if plen < 1 or plen > 24:
            self.len = b'\x00'
            self.payload = b''
            return False
        self.len = len(payload).to_bytes(1,'big')
        self.payload = payload
        return True
            
        





