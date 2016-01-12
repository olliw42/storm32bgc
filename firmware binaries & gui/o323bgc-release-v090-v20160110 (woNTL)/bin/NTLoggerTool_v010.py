#!/usr/bin/env python

whichUiToUse = 'py_ow'
#whichUiToUse = 'py'
#whichUiToUse = 'ui'


ApplicationStr = "NT DataLogger"
VersionStr = "10. Jan. 2016 v0.10"
IniFileStr = "./NTLoggerTool.ini"


import sys
import struct
from math import sqrt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QFile, Qt, QSettings
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QColorDialog, QDialog,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QToolButton,
                             QStyleFactory, QStyle, QListWidgetItem)
from PyQt5.QtGui import QPalette, QColor, QFont, QFontInfo, QFontMetrics, QFontDatabase

#pyuic5 input.ui -o output.py
if( whichUiToUse=='py_ow' ):
    import NTLoggerTool_ui_ow
    wMainWindow = NTLoggerTool_ui_ow.Ui_wWindow
elif( whichUiToUse=='py' ):
    import NTLoggerTool_ui
    wMainWindow = NTLoggerTool_ui.Ui_wWindow
else:
    from PyQt5.uic import loadUiType
    wMainWindow, _ = loadUiType('NTLoggerTool_ui.ui')

import numpy as np
from io import StringIO #this is needed to make np.loadtxt to work
import pyqtgraph as pg

#import cv2


###################################################################
# cDataLogger, cVibe
###################################################################

def trimStrWithCharToLength(s,len_,c):
    while len(s)<len_: s = s + c
    return s

def strwt(s): return str(s)+"\t"

def strwn(s): return str(s)+"\n"


class cPX4:
    # PX4BIN constants & field macros
    cSTX  = b'\xA3\x95' #bytes.fromhex('A395')
    cFMT  = b'\x80'
    cGPS  = b'\x82'
    cVIBE = b'\xBD' #128+61 = 189 = 0xBD, MP just looks for VIBE, not number!!!

    cSTAT = b'\xEA' #234 = 0cEA
    cAHRS = b'\xEB'
    cANG  = b'\xEC'
    cCNTL = b'\xED'
    cRCIN = b'\xEF'
    cRC2  = b'\xF0'

    cPERF = b'\xF1'
    cRAW1 = b'\xF2'
    cRAW2 = b'\xF3'
    cIMU1 = b'\xF4'
    cIMU2 = b'\xF5'
    cPID  = b'\xF7'
    cMOT  = b'\xF8'

    #this is a macro for generating a FMT list entry
    def PX4FMT(self,id_,len_,cid,format_,list_):
        return self.cSTX + self.cFMT + id_ + bytes([3+len_]) + (
              trimStrWithCharToLength(cid,4,"\0") +
              trimStrWithCharToLength(format_,16,"\0") +
              trimStrWithCharToLength(list_,64,"\0")        ).encode('utf-8')

    def FMT_FMT(self):
        return self.PX4FMT( self.cFMT, 0x59, 'FMT', 'BBnNZ', 'Type,Length,Name,Format,Columns' )

    #def FMT_GPS(self,):
    #    return self.PX4FMT( cGPS, 0x2D, 'GPS', 'BIHBcLLeeEefI', 'Status,TimeMS,Week,NSats,HDop,Lat,Lng,RelAlt,Alt,Spd,GCrs,VZ,T' )

    #def GPS(self,):
    #    return cPX4MP_STX + cPX4MP_GPS + struct.pack( '<',
    #         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5] )

    def FMT_STAT(self):
        return self.PX4FMT( self.cSTAT, 4 + (1)*4+(6)*2, 'STAT', 'IIHHHHHC', 'TimeMS,i,millis,State,Status,Status2,BusError,Voltage' )

    def STAT(self,tupel):
        return self.cSTX + self.cSTAT + struct.pack( '<IIHHHHHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7] )

    def FMT_AHRS(self):
        return self.PX4FMT( self.cAHRS, 4 + (3+3+3+1+1)*2, 'AHRS', 'Ihhhhhhccccc', 'TimeMS,GyroX,GyroY,GyroZ,AccX,AccY,AccZ,Rx,Ry,Rz,AccAbs,AccConf' )

    def AHRS(self,tupel):
        return self.cSTX + self.cAHRS + struct.pack( '<Ihhhhhhhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7],tupel[8],tupel[9],tupel[10] )

    def FMT_ANG(self):
        return self.PX4FMT( self.cANG, 4 + (6)*2, 'ANG', 'Icccccc', 'TimeMS,Pitch,Roll,Yaw,Pitch2,Roll2,Yaw2' )

    def ANG(self,tupel):
        return self.cSTX + self.cANG + struct.pack( '<Ihhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6] )

    def FMT_CNTL(self):
        return self.PX4FMT( self.cCNTL, 4 + (3)*2, 'CNTL', 'Iccc', 'TimeMS,PCntrl,RCntrl,YCntrl' )

    def CNTL(self,tupel):
        return self.cSTX + self.cCNTL + struct.pack( '<Ihhh',
         tupel[0],tupel[1],tupel[2],tupel[3] )

    def FMT_RCIN(self):
        return self.PX4FMT( self.cRCIN, 4 + (3)*2, 'RCIN', 'Ihhh', 'TimeMS,RcInPitch,RcInRoll,RcInYaw' )

    def RCIN(self,tupel):
        return self.cSTX + self.cRCIN + struct.pack( '<Ihhh',
         tupel[0],tupel[1],tupel[2],tupel[3] )

    def FMT_RC2(self):
        return self.PX4FMT( self.cRC2, 4 + (8)*2, 'RC2', 'Ihhhhhhhh', 'TimeMS,PanMode,StandBy,IRCamera,ReCenter,Script,Scr2,Scr3,Scr4' )

    def RC2(self,tupel):
        return self.cSTX + self.cRC2 + struct.pack( '<Ihhhhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7],tupel[8] )

    def FMT_VIBE(self):
        return self.PX4FMT( self.cVIBE, 4 + (3+3+3)*4, 'VIBE','IfffIIIfff', 'TimeMS,VibeX,VibeY,VibeZ,Clip0,Clip1,Clip2,ax,ay,az' )

    def VIBE(self,tupel):
        return self.cSTX + self.cVIBE + struct.pack( '<IfffIIIfff',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7],tupel[8],tupel[9] )

    def FMT_STAT_2(self):
        return self.PX4FMT( self.cSTAT, 4 + (5)*2, 'STAT', 'IHHHHC', 'TimeMS,State,Status,Status2,BusError,Voltage' )

    def STAT_2(self,tupel):
        return self.cSTX + self.cSTAT + struct.pack( '<IHHHHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5] )

    def FMT_PERF(self):
        return self.PX4FMT( self.cPERF, 4 + (7)*2, 'PERF', 'IHHHHHHH', 'TimeMS,Imu1rx,Imu1done,PIDdone,Motdone,Imu2rx,Imu2done,Loopdone' )

    def PERF(self,tupel):
        return self.cSTX + self.cPERF + struct.pack( '<IHHHHHHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7] )

    def FMT_RAW1(self):
        return self.PX4FMT( self.cRAW1, 4 + (6)*2, 'RAW1', 'Ihhhhhh', 'TimeMS,ax1raw,ay1raw,az1raw,gx1raw,gy1raw,gz1raw' )

    def RAW1(self,tupel):
        return self.cSTX + self.cRAW1 + struct.pack( '<Ihhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6] )

    def FMT_RAW2(self):
        return self.PX4FMT( self.cRAW2, 4 + (6)*2, 'RAW2', 'Ihhhhhh', 'TimeMS,ax2raw,ay2raw,az2raw,gx2raw,gy2raw,gz2raw' )

    def RAW2(self,tupel):
        return self.cSTX + self.cRAW2 + struct.pack( '<Ihhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6] )

    def FMT_IMU1(self):
        return self.PX4FMT( self.cIMU1, 4 + (8)*2, 'IMU1', 'IhhhhhhCH', 'TimeMS,ax1,ay1,az1,gx1,gy1,gz1,T1,Imu1State' )

    def IMU1(self,tupel):
        return self.cSTX + self.cIMU1 + struct.pack( '<IhhhhhhHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7],tupel[8] )

    def FMT_IMU2(self):
        return self.PX4FMT( self.cIMU2, 4 + (8)*2, 'IMU2', 'IhhhhhhCH', 'TimeMS,ax1,ay1,az1,gx1,gy1,gz1,T1,Imu1State' )

    def IMU2(self,tupel):
        return self.cSTX + self.cIMU2 + struct.pack( '<IhhhhhhHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7],tupel[8] )

    def FMT_PID(self):
        return self.PX4FMT( self.cPID, 4 + (6)*2, 'PID', 'Icccccc', 'TimeMS,PIDPitch,PIDRoll,PIDYaw,PIDMotPitch,PIDMotRoll,PIDMotYaw' )

    def PID(self,tupel):
        return self.cSTX + self.cPID + struct.pack( '<Ihhhhhh',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6] )

    def FMT_MOT(self):
        return self.PX4FMT( self.cMOT, 4 + (7)*2, 'MOT', 'IHHHHHHH', 'TimeMS,MotFlags,VmaxPitch,MotPitch,VmaxRoll,MotRoll,VmaxYaw,MotYaw' )

    def MOT(self,tupel):
        return self.cSTX + self.cMOT + struct.pack( '<IHHHHHHH',
         tupel[0],tupel[1],tupel[2],tupel[3],tupel[4],tupel[5],tupel[6],tupel[7] )


class cVibe:
    # t_acc should be a tupel
    # dt is in seconds

    def __init__(self):
        # super() calls a method of the parent class
        # https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        ##super(self.__class__, self).__init__() #this is to call the init of the paranet class
        self.vibeFloor = [0,0,0]
        self.vibeSqr = [0,0,0]
        self.hpfFrequenzy = 5.0 #5Hz
        self.lpfFrequenzy = 2.0 #2Hz
        self.initialized = False

    def update(self, t_acc, dt):
        if not self.initialized:
            self.initialized = True
            self.vibeFloor = list(t_acc)
        hpf_dt = (6.28*self.hpfFrequenzy)*dt
        lpf_dt = (6.28*self.lpfFrequenzy)*dt
        vibe = [0.0,0.0,0.0];
        for n in range(0,3):
            self.vibeFloor[n] += hpf_dt * ( t_acc[n] - self.vibeFloor[n] )
            dv = ( t_acc[n] - self.vibeFloor[n] )
            self.vibeSqr[n] += lpf_dt * ( dv*dv - self.vibeSqr[n] )
            if self.vibeSqr[n] <= 0.0:
                vibe[n] = 0.0;
            else:
                vibe[n] = sqrt(self.vibeSqr[n])
        return vibe


cCMD_RES = 0x50 #'RES ';
cCMD_SET = 0x40 #'SET ';
cCMD_GET = 0x30 #'GET ';
cCMD_TRG = 0x10 #'TRG ';
cCMD_CMD = 0x00 #'CMD ';

cID_ALL  = 0  #'ALL  ';
cID_IMU1 = 1  #'IMU1 '
cID_IMU2 = 2  #'IMU2 '
cID_MOTA = 3  #'MOTA ';
cID_LOG  = 11 #'LOG  ';

cIDBYTE_LOG_AccGyro1RawData = 32 #'CMD ';'LOG  '; AccGyro1RawData
cIDBYTE_LOG_AccGyro2RawData = 33 #'CMD ';'LOG  '; AccGyro2RawData
cIDBYTE_LOG_AccGyroData     = 34 #'CMD ';'LOG  '; AccGyroData
cIDBYTE_LOG_PidData         = 35 #'CMD ';'LOG  '; PidData
cIDBYTE_LOG_ParameterData   = 36 #'CMD ';'LOG  '; ParameterData

class cDataLogger:

    def readLogFile(self,loadLogThread,fileName,createTraffic,createPX4bin):
        try:
            F = open(fileName, 'rb')
        except:
            return '','',''

        #this is the header which preludes each data packet, 1+1+4+1+1+1 = 9 bytes, stx = 'R'
        headerStruct = struct.Struct('=BBIBBB')
        stx,size,timestamp,cmd,idbyte,cmdbyte = 0,0,0,0,0,0

        setMotorAllStruct = struct.Struct('=BBhBhBh')
        Flags,VmaxPitch,AnglePitch,VmaxRoll,AngleRoll,VmaxYaw,AngleYaw = 0,0,0,0,0,0,0

        setLoggerStruct = struct.Struct('=I'+'BBBBBBB'+'HHHHH'+'hhhhhh')
        TimeStamp32 = 0
        Imu1received,Imu1done,PIDdone,Motorsdone,Imu2received,Imu2done,Loopdone = 0,0,0,0,0,0,0
        State,Status,Status2,ErrorCnt,Voltage = 0,0,0,0,0
        Imu1AnglePitch,Imu1AngleRoll,Imu1AngleYaw,Imu2AnglePitch,Imu2AngleRoll,Imu2AngleYaw = 0,0,0,0,0,0

        cmdAccGyroStruct = struct.Struct('=hhhhhhhB'+'hhhhhhhB')
        ax1,ay1,az1,gx1,gy1,gz1,temp1,ImuState1 = 0,0,0,0,0,0,0,0
        ax2,ay2,az2,gx2,gy2,gz2,temp2,ImuState2 = 0,0,0,0,0,0,0,0

        cmdPidStruct = struct.Struct('=hhhhhh')
        PIDCntrlPitch,PIDCntrlRoll,PIDCntrlYaw,PIDMotorCntrlPitch,PIDMotorCntrlRoll,PIDMotorCntrlYaw = 0,0,0,0,0,0

        cmdAccGyroRawStruct = struct.Struct('=hhhhhh')
        ax1raw,ay1raw,az1raw,gx1raw,gy1raw,gz1raw = 0,0,0,0,0,0
        ax2raw,ay2raw,az2raw,gx2raw,gy2raw,gz2raw = 0,0,0,0,0,0

        cmdParameterStruct = struct.Struct('=HHH16s')
        ParameterAdr,ParameterValue,ParameterFormat,ParameterNameStr = 0,0,0,''

        datalog = []
        datalog.append( "Time" )
        datalog.append( "\tImu1rx\tImu1done\tPIDdone\tMotdone\tImu2rx\tImu2done\tLoopdone" )
        datalog.append( "\tState\tStatus\tStatus2\tErrorCnt\tVoltage" )
        datalog.append( "\tax1raw\tay1raw\taz1raw\tgx1raw\tgy1raw\tgz1raw" )
        datalog.append( "\tax2raw\tay2raw\taz2raw\tgx2raw\tgy2raw\tgz2raw" )
        datalog.append( "\tax1\tay1\taz1\tgx1\tgy1\tgz1\tT1\tImu1State" )
        datalog.append( "\tax2\tay2\taz2\tgx2\tgy2\tgz2\tT2\tImu2State" )
        datalog.append( "\tImu1Pitch\tImu1Roll\tImu1Yaw\tImu2Pitch\tImu2Roll\tImu2Yaw" )
        datalog.append( "\tPIDPitch\tPIDRoll\tPIDYaw\tPIDMotPitch\tPIDMotRoll\tPIDMotYaw" )
        datalog.append( "\tMotFlags\tVmaxPitch\tMotPitch\tVmaxRoll\tMotRoll\tVmaxYaw\tMotYaw" )
        datalog.append( "\tVibeX1\tVibeY1\tVibeZ1\tVibeX2\tVibeY2\tVibeZ2" )
        datalog.append( "\n" )
        datalog.append( "[ms]" )
        datalog.append( "\t[us]\t[us]\t[us]\t[us]\t[us]\t[us]\t[us]" )
        datalog.append( "\t[int]\t[hex]\t[hex]\t[int]\t[V]" )
        datalog.append( "\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]" )
        datalog.append( "\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]" )
        datalog.append( "\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]\t[o]\t[hex]" )
        datalog.append( "\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]\t[o]\t[hex]" )
        datalog.append( "\t[deg]\t[deg]\t[deg]\t[deg]\t[deg]\t[deg]" )
        datalog.append( "\t[deg]\t[deg]\t[deg]\t[deg]\t[deg]\t[deg]" )
        datalog.append( "\t[hex]\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]" )
        datalog.append( "\t[int]\t[int]\t[int]\t[int]\t[int]\t[int]" )
        datalog.append( "\n" )

        trafficlog = []

        px4binlog = []
        if( createPX4bin ):
            PX4 = cPX4()
            px4binlog.append( PX4.FMT_FMT() )
            px4binlog.append( PX4.FMT_STAT_2() )
            px4binlog.append( PX4.FMT_PERF() )
            px4binlog.append( PX4.FMT_RAW1() )
            px4binlog.append( PX4.FMT_RAW2() )
            px4binlog.append( PX4.FMT_IMU1() )
            px4binlog.append( PX4.FMT_IMU2() )
            px4binlog.append( PX4.FMT_ANG() )
            px4binlog.append( PX4.FMT_PID() )
            px4binlog.append( PX4.FMT_MOT() )
            px4binlog.append( PX4.FMT_VIBE() )

        byte_counter = 0
        fileInfo = QFile(fileName)
        byte_max = fileInfo.size()
        byte_percentage = 0
        byte_step = 5

        trafficlog_counter = 0
        TimeStamp32_last = -1
        initialized = False
        datalog_timestamp_start = -1

        vibe1 = cVibe()
        vibe2 = cVibe()

        while 1:
            if( loadLogThread.canceled ): break
            #print( byte_counter )

            header = F.read(9)
            if header == '' or len(header) != 9:
                break
            byte_counter += 9

            #------------------------------------------
            #Header, read header data into proper fields

            stx, size, timestamp, cmd, idbyte, cmdbyte = headerStruct.unpack(header)
            if stx != ord('R'):
                cmd = -1
                idbyte = -1
                cmdbyte = -1

            #------------------------------------------
            #Data, read remaining data into proper fields

            payload = F.read(size-9)
            if payload == '' or len(payload) != size-9:
                break
            byte_counter += size-9

            #------------------------------------------
            #read data send with R cmd

            if cmd==cCMD_RES: #0x50 # 'RES ';
                pass
            elif cmd==cCMD_SET: #0x40 #'SET ';
                if idbyte==cID_MOTA: #3 #'SET ';'MOTA ';
                    (Flags,VmaxPitch,AnglePitch,VmaxRoll,AngleRoll,VmaxYaw,AngleYaw
                     ) = setMotorAllStruct.unpack(payload)
                elif idbyte==cID_LOG: #11 #'SET ';'LOG  ';
                    (TimeStamp32,
                     Imu1received,Imu1done,PIDdone,Motorsdone,Imu2received,Imu2done,Loopdone,
                     State,Status,Status2,ErrorCnt,Voltage,
                     Imu1AnglePitch,Imu1AngleRoll,Imu1AngleYaw,Imu2AnglePitch,Imu2AngleRoll,Imu2AngleYaw,
                     ) = setLoggerStruct.unpack(payload)
            elif cmd==cCMD_GET: #0x30 #'GET ';
                pass
            elif cmd==cCMD_TRG: #0x10: #'TRG ';
                if idbyte==cID_ALL: #'TRG ';'ALL  ';
                    Flags,VmaxPitch,AnglePitch,VmaxRoll,AngleRoll,VmaxYaw,AngleYaw = 0,0,0,0,0,0,0
                    TimeStamp32 = 0
                    Imu1received,Imu1done,PIDdone,Motorsdone,Imu2received,Imu2done,Loopdone = 0,0,0,0,0,0,0
                    State,Status,Status2,ErrorCnt,Voltage = 0,0,0,0,0
                    Imu1AnglePitch,Imu1AngleRoll,Imu1AngleYaw,Imu2AnglePitch,Imu2AngleRoll,Imu2AngleYaw = 0,0,0,0,0,0
                    ax1,ay1,az1,gx1,gy1,gz1,temp1,ImuState1 = 0,0,0,0,0,0,0,0
                    ax2,ay2,az2,gx2,gy2,gz2,temp2,ImuState2 = 0,0,0,0,0,0,0,0
                    PIDCntrlPitch,PIDCntrlRoll,PIDCntrlYaw,PIDMotorCntrlPitch,PIDMotorCntrlRoll,PIDMotorCntrlYaw = 0,0,0,0,0,0
                    ax1raw,ay1raw,az1raw,gx1raw,gy1raw,gz1raw = 0,0,0,0,0,0
                    ax2raw,ay2raw,az2raw,gx2raw,gy2raw,gz2raw = 0,0,0,0,0,0
            elif cmd==cCMD_CMD: #0x00 #'CMD ';
                if idbyte==cID_LOG:
                    if cmdbyte==cIDBYTE_LOG_AccGyro1RawData: #'CMD ';'LOG  '; AccGyro1RawData
                        (ax1raw,ay1raw,az1raw,gx1raw,gy1raw,gz1raw
                         ) = cmdAccGyroRawStruct.unpack(payload)
                    elif cmdbyte==cIDBYTE_LOG_AccGyro2RawData: #'CMD ';'LOG  '; AccGyro2RawData
                        (ax2raw,ay2raw,az2raw,gx2raw,gy2raw,gz2raw
                         ) = cmdAccGyroRawStruct.unpack(payload)
                    elif cmdbyte==cIDBYTE_LOG_AccGyroData: #'CMD ';'LOG  '; AccGyroData
                        (ax1,ay1,az1,gx1,gy1,gz1,temp1,ImuState1,
                         ax2,ay2,az2,gx2,gy2,gz2,temp2,ImuState2
                         ) = cmdAccGyroStruct.unpack(payload)
                    elif cmdbyte==cIDBYTE_LOG_PidData: #'CMD ';'LOG  '; PidData
                        (PIDCntrlPitch,PIDCntrlRoll,PIDCntrlYaw,PIDMotorCntrlPitch,PIDMotorCntrlRoll,PIDMotorCntrlYaw
                         ) = cmdPidStruct.unpack(payload)
                    elif cmdbyte==cIDBYTE_LOG_ParameterData: #'CMD ';'LOG  '; ParameterData
                        (ParameterAdr,ParameterValue,ParameterFormat,ParameterNameStr
                         ) = cmdParameterStruct.unpack(payload)

            #------------------------------------------
            #NTbus traffic log
            if( createTraffic or trafficlog_counter<500 ):
                tl = str(trafficlog_counter)
                ts = str(timestamp)
                while len(ts)<10: ts = '0'+ts
                trafficlog.append( tl+'\t'+ts+'  ' )

                if cmd==cCMD_RES:   trafficlog.append( 'RES ' )
                elif cmd==cCMD_SET: trafficlog.append( 'SET ' )
                elif cmd==cCMD_GET: trafficlog.append( 'GET ' )
                elif cmd==cCMD_TRG: trafficlog.append( 'TRG ' )
                elif cmd==cCMD_CMD: trafficlog.append( 'CMD ' )
                else:               trafficlog.append( '??? ' )

                if idbyte==cID_ALL:    trafficlog.append( 'ALL  ' )
                elif idbyte==cID_IMU1: trafficlog.append( 'IMU1 ' )
                elif idbyte==cID_IMU2: trafficlog.append( 'IMU2 ' )
                elif idbyte==cID_MOTA: trafficlog.append( 'MOTA ' )
                elif idbyte==cID_LOG:  trafficlog.append( 'LOG  ' )
                else:                  trafficlog.append( '???  ' )

                if stx != ord('R'):
                    trafficlog.append( ' ERROR' )
                else:
                    if cmd==cCMD_RES: #0x50 # 'RES ';
                        pass
                    elif cmd==cCMD_SET: #0x40 #'SET ';
                        if idbyte==cID_MOTA: #3 #'MOTA ';
                            trafficlog.append( '0x'+'{:02X}'.format(Flags) )
                            trafficlog.append( ' '+str(VmaxPitch)+' '+str(AnglePitch) )
                            trafficlog.append( ' '+str(VmaxRoll)+' '+str(AngleRoll) )
                            trafficlog.append( ' '+str(VmaxYaw)+' '+str(AngleYaw) )
                        elif idbyte==cID_LOG: #11 #'LOG  ';
                            trafficlog.append( str(TimeStamp32) )
                            if TimeStamp32_last >= 0:
                                trafficlog.append( ' ('+str(TimeStamp32-TimeStamp32_last)+')' )
                    elif cmd==cCMD_GET: #0x30 #'GET ';
                        pass
                    elif cmd==cCMD_TRG: #0x10 #'TRG ';
                        pass
                    elif cmd==cCMD_CMD: #0x00 #'CMD ';
                        trafficlog.append( str(cmdbyte) )
                        if cmdbyte==cIDBYTE_LOG_ParameterData: #'CMD ';'LOG  '; ParameterData
                            if ParameterAdr==65535:
                                trafficlog.append( '\t'+str(ParameterNameStr, "utf-8") )
                            else:
                                trafficlog.append( '\t'+str(ParameterAdr)+'\t'+str(ParameterNameStr, "utf-8")+'\t' )
                                if ParameterFormat==4: #MAV_PARAM_TYPE_INT16 = 4
                                    if ParameterValue>32768: ParameterValue -= 65536
                                trafficlog.append( str(ParameterValue) )

                trafficlog.append( '\n' )
                trafficlog_counter += 1

            #if trafficlog_counter>100: break

            #------------------------------------------
            #NTbus traffic data frame analyzer

            frameerror = 0
            dt = 0
            if cmd==cCMD_SET and idbyte==cID_LOG:  #'SET ';#'LOG  ';
                if TimeStamp32_last>=0:
                    if TimeStamp32 - TimeStamp32_last > 1700:
                        frameerror = 1
                dt = 1.0E-6 * (TimeStamp32 - TimeStamp32_last)
                TimeStamp32_last = TimeStamp32

            if( createTraffic or trafficlog_counter<500 ):
                if frameerror>0:
                    trafficlog.append( '*******************   ERROR: lost frame(s)   ****************************************************\n' )

            #------------------------------------------
            #NTbus data and bin log values

            if cmd==cCMD_SET and idbyte==cID_LOG and frameerror==0: #'SET ';#'LOG  ';
                if not initialized:
                    datalog_timestamp_start = TimeStamp32
                initialized = True
                Time = TimeStamp32 - datalog_timestamp_start

                ftemp1 = temp1/340.0 + 36.53
                ftemp2 = temp2/340.0 + 36.53

                acc1 = (9.81E-4*ax1raw, 9.81E-4*ay1raw, 9.81E-4*az1raw)
                vibe1_values = vibe1.update( acc1, dt )
                vibe2_values = vibe2.update( (9.81E-4*ax2raw, 9.81E-4*ay2raw, 9.81E-4*az2raw), dt )

            #------------------------------------------
            #NTbus data log

                dataline = ''

                dataline +=  '{:.1f}'.format(0.001*Time) + "\t"
                dataline +=  str(10*Imu1received) + "\t"
                dataline +=  str(10*Imu1done) + "\t"
                dataline +=  str(10*PIDdone) + "\t"
                dataline +=  str(10*Motorsdone) + "\t"
                dataline +=  str(10*Imu2received) + "\t"
                dataline +=  str(10*Imu2done) + "\t"
                dataline +=  str(10*Loopdone) + "\t"

                dataline +=  str(State) + "\t"
                dataline +=  str(Status) + "\t"
                dataline +=  str(Status2) + "\t"
                dataline +=  str(ErrorCnt) + "\t"
                fVoltage = Voltage #in a hope that ensures that Voltage remains a H = ushort
                dataline +=  '{:.3f}'.format(0.001*fVoltage) + "\t"

                dataline +=  str(ax1raw) + "\t" + str(ay1raw) + "\t" + str(az1raw) + "\t"
                dataline +=  str(gx1raw) + "\t" + str(gy1raw) + "\t" + str(gz1raw) + "\t"
                dataline +=  str(ax2raw) + "\t" + str(ay2raw) + "\t" + str(az2raw) + "\t"
                dataline +=  str(gx2raw) + "\t" + str(gy2raw) + "\t" + str(gz2raw) + "\t"

                dataline +=  str(ax1) + "\t" + str(ay1) + "\t" + str(az1) + "\t"
                dataline +=  str(gx1) + "\t" + str(gy1) + "\t" + str(gz1) + "\t"
                dataline +=  '{:.2f}'.format(ftemp1) + "\t"
                dataline +=  str(ImuState1) + "\t"
                dataline +=  str(ax2) + "\t" + str(ay2) + "\t" + str(az2) + "\t"
                dataline +=  str(gx2) + "\t" + str(gy2) + "\t" + str(gz2) + "\t"
                dataline +=  '{:.2f}'.format(ftemp2) + "\t"
                dataline +=  str(ImuState2) + "\t"

                dataline +=  '{:.2f}'.format( 0.01 * Imu1AnglePitch ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * Imu1AngleRoll ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * Imu1AngleYaw ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * Imu2AnglePitch ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * Imu2AngleRoll ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * Imu2AngleYaw ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDCntrlPitch ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDCntrlRoll ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDCntrlYaw ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDMotorCntrlPitch ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDMotorCntrlRoll ) + "\t"
                dataline +=  '{:.2f}'.format( 0.01 * PIDMotorCntrlYaw ) + "\t"

                dataline +=  str(Flags) + "\t"
                dataline +=  str(VmaxPitch) + "\t" + str(AnglePitch) + "\t"
                dataline +=  str(VmaxRoll) + "\t"  + str(AngleRoll) + "\t"
                dataline +=  str(VmaxYaw) + "\t"   + str(AngleYaw) + "\t"

                dataline +=  '{:.2f}'.format(vibe1_values[0]) + "\t"
                dataline +=  '{:.2f}'.format(vibe1_values[1]) + "\t"
                dataline +=  '{:.2f}'.format(vibe1_values[2]) + "\t"
                dataline +=  '{:.2f}'.format(vibe2_values[0]) + "\t"
                dataline +=  '{:.2f}'.format(vibe2_values[1]) + "\t"
                dataline +=  '{:.2f}'.format(vibe2_values[2]) + "\n"

                datalog.append(dataline)

            #------------------------------------------
            #NTbus px4 bin log
                if( createPX4bin ):
                    px4binlog.append(PX4.STAT_2(
                        (Time, State, Status, Status2, ErrorCnt, Voltage) ))
                    px4binlog.append(PX4.PERF(
                        (Time, 10*Imu1received, 10*Imu1done, 10*PIDdone, 10*Motorsdone, 10*Imu2received, 10*Imu2done, 10*Loopdone) ))
                    px4binlog.append(PX4.RAW1(
                        (Time, ax1raw, ay1raw, az1raw, gx1raw, gy1raw, gz1raw) ))
                    px4binlog.append(PX4.RAW2(
                        (Time, ax2raw, ay2raw, az2raw, gx2raw, gy2raw, gz2raw) ))
                    px4binlog.append(PX4.IMU1(
                        (Time, ax1, ay1, az1, gx1, gy1, gz1, int(100.0*ftemp1), ImuState1) ))
                    px4binlog.append(PX4.IMU2(
                        (Time, ax2, ay2, az2, gx2, gy2, gz2, int(100.0*ftemp2), ImuState2) ))
                    px4binlog.append(PX4.ANG(
                        (Time, Imu1AnglePitch, Imu1AngleRoll, Imu1AngleYaw, Imu2AnglePitch, Imu2AngleRoll, Imu2AngleYaw) ))
                    px4binlog.append(PX4.PID(
                        (Time, PIDCntrlPitch, PIDCntrlRoll, PIDCntrlYaw, PIDMotorCntrlPitch, PIDMotorCntrlRoll, PIDMotorCntrlYaw) ))
                    px4binlog.append(PX4.MOT(
                        (Time, Flags, VmaxPitch, AnglePitch, VmaxRoll, AngleRoll, VmaxYaw, AngleYaw) ))
                    px4binlog.append(PX4.VIBE(
                        (Time, vibe1_values[0],vibe1_values[1],vibe1_values[2], 0, 0, 0, acc1[0],acc1[1],acc1[2]) ))

            if (100*byte_counter)/byte_max>byte_percentage:
                loadLogThread.emitProgress(byte_percentage)
                byte_percentage += byte_step

        #end of while 1:
        F.close();
        loadLogThread.emitProgress(100)
        return trafficlog, datalog, px4binlog




###################################################################
# cMain
###################################################################

class cLoadLogThread(QThread):

    progress = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.fileName = ''
        self.createTraffic = False
        self.createPX4bin = False
        self.traffic = ''
        self.data = ''
        self.px4bin = []
        self.progressValue = ''
        self.canceled = False

    def __del__(self):
        self.wait()

    def setFile(self,_fileName,_createTraffic=False,_createPX4bin=False):
        self.fileName = _fileName
        self.createTraffic = _createTraffic
        self.createPX4bin = _createPX4bin

    def run(self):
        self.progressValue = ''
        self.canceled = False
        DataLogger = cDataLogger()
        traffic, data, self.px4bin = DataLogger.readLogFile(self, self.fileName, self.createTraffic, self.createPX4bin)
        self.traffic = "".join(traffic)
        self.data = "".join(data)

    def cancel(self):
        self.canceled = True

    def emitProgress(self,progress_value):
        self.progressValue = progress_value
        self.progress.emit()

    def clearUnrequired(self):
        self.traffic = ''
        self.data = ''
        self.px4bin = []


class cMain(QMainWindow,wMainWindow):

    appPalette = 'Fusion'

    def __init__(self, _winScale, _appPalette):
        super(self.__class__, self).__init__()

        if( whichUiToUse=='py_ow' ):
            self.setupUi(self, _winScale)
        else:
            self.setupUi(self)

        appPalette = _appPalette #this is needed to allow writing into ini file

        self.actionLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.actionSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.actionClear.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))

        self.bLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.bSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.bCancelLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))

        self.bPlaybackBegin.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.bPlaybackSkipBackward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.bPlaybackPlayStop.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.bPlaybackSkipForward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.bPlaybackEnd.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.wGraphZoomFactor.addItems( ['100 %','10 %','1 %','30 s','10 s','5 s','2 s','1 s','100 ms'] )
        self.wGraphZoomFactor.setCurrentIndex( 3 )
        self.wPlaybackSpeedFactor.addItems( ['8 x','4 x','2 x','1 x','1/2 x','1/4 x','1/8 x','1/8 x'] )
        self.wPlaybackSpeedFactor.setCurrentIndex( 3 )

        self.wProgressBar.hide()
        self.bCancelLoad.hide()
        self.fileDialogDir = ''

        self.loadLogThread = cLoadLogThread()
        self.loadLogThread.finished.connect(self.loadLogFileDone)
        self.loadLogThread.progress.connect(self.loadLogFileProgress)

        self.currentLogFileName = '' #name of file currently in buffers
        self.px4binlog = []  #traffic and data are stored in tab fields!
        self.nparraylog = ''
        self.nparraylog_initialized = False

        #self.pqGraphicsWindow = pg.GraphicsWindow()
        self.pqGraphicsWindow = pg.GraphicsLayoutWidget() #this is needed instead of selfpqPlotWidget = pg.PlotWidget() for the mouse/vb to work
        self.pqGraphicsWindow.ci.setContentsMargins(3,3,9,3)
        #self.pqGraphicsWindow.setBackground(None)
        self.wGraphAreaLayout.addWidget(self.pqGraphicsWindow)

        self.pqPlotWidget = self.pqGraphicsWindow.addPlot()#(row=1, col=0) not needed with only one item
        self.pqPlotWidget.setLabel('bottom', 'Time', units='s')
        self.pqPlotWidget.showGrid(x=True, y=True, alpha=0.33)
        self.pqPlotWidget.setXRange( 0.0, 1.0 )
        self.pqPlotWidget.setYRange( 0.0, 1.0 )

        self.pgGraphTimeLine = pg.InfiniteLine(angle=90, movable=False)
        #self.pqPlotWidget.addItem(self.pgGraphTimeLine, ignoreBounds=True)

        self.wGraphLegend.setText( '' )
        col = pg.mkColor( pg.getConfigOption('foreground') )
        colstr = pg.colorStr(col)[:6]
        self.wGraphCursorFormatStr = "<span style='color: #"+colstr+"'>x = %0.4f, y = %0.4f</span>"
        self.updateGraphCursor(0,0)
        self.wGraphTimeFormatStr = "<span style='color: #"+colstr+"'>%s</span>"
        self.updateGraphTimeLabel( 0.0 )
        self.updateGraphTime( 0.0 )

        self.pqGraphicsWindow.scene().sigMouseMoved.connect(self.updateGraphCursorEvent)
        self.pqPlotWidget.sigXRangeChanged.connect(self.updateGraphRangeChangedEvent)
        self.wGraphTimeSlider.valueChanged.connect(self.updateGraphTimeSliderValueChangedEvent)

        self.logColumnList = [
            "Time", #0
            "Imu1rx","Imu1done","PIDdone","Motdone","Imu2rx","Imu2done","Loopdone", #1-7
            "State","Status","Status2","ErrorCnt","Voltage", #8-12
            "ax1raw","ay1raw","az1raw","gx1raw","gy1raw","gz1raw", #13-18
            "ax2raw","ay2raw","az2raw","gx2raw","gy2raw","gz2raw", #19-
            "ax1","ay1","az1","gx1","gy1","gz1","T1","Imu1State", #25-
            "ax2","ay2","az2","gx2","gy2","gz2","T2","Imu2State", #33-
            "Imu1Pitch","Imu1Roll","Imu1Yaw","Imu2Pitch","Imu2Roll","Imu2Yaw", #41-
            "PIDPitch","PIDRoll","PIDYaw","PIDMotPitch","PIDMotRoll","PIDMotYaw", #47-
            "MotFlags","VmaxPitch","MotPitch","VmaxRoll","MotRoll","VmaxYaw","MotYaw", #53-
            "VibeX1","VibeY1","VibeZ1","VibeX2","VibeY2","VibeZ2", #60-
        ]
        cl = self.logColumnList
        self.graphSelectorEntryList = [
            ['Performance',[cl.index("Imu1rx"),cl.index("Imu1done"),cl.index("PIDdone"),
                            cl.index("Motdone"),cl.index("Imu2rx"),cl.index("Imu2done"),cl.index("Loopdone")] ],
            ['Imu1 Pitch,Roll,Yaw',[cl.index("Imu1Pitch"),cl.index("Imu1Roll"),cl.index("Imu1Yaw")] ],
            ['Imu2 Pitch,Roll,Yaw',[cl.index("Imu2Pitch"),cl.index("Imu2Roll"),cl.index("Imu2Yaw")] ],
            ['PID Pitch,Roll,Yaw',[cl.index("PIDPitch"),cl.index("PIDRoll"),cl.index("PIDYaw")] ],
            ['State',[cl.index('State')]],
            ['Error',[cl.index('ErrorCnt')]],
            ['Voltage',[cl.index('Voltage')]],
            ['Acc1',[cl.index("ax1"),cl.index("ay1"),cl.index("az1")]],
            ['Gyro1',[cl.index("gx1"),cl.index("gy1"),cl.index("gz1")]],
            ['Acc2',[cl.index("ax2"),cl.index("ay2"),cl.index("az2")]],
            ['Gyro2',[cl.index("gx2"),cl.index("gy2"),cl.index("gz2")]],
            ['Temp 1+2',[cl.index("T1"),cl.index("T2")]],
            ['PID Mot Pitch,Roll,Yaw',[cl.index("PIDMotPitch"),cl.index("PIDMotRoll"),cl.index("PIDMotYaw")]],
            ['Acc1 raw',[cl.index("ax1raw"),cl.index("ay1raw"),cl.index("az1raw")]],
            ['Gyro1 raw',[cl.index("gx1raw"),cl.index("gy1raw"),cl.index("gz1raw")]],
            ['Acc2 raw',[cl.index("ax2raw"),cl.index("ay2raw"),cl.index("az2raw")]],
            ['Gyro2 raw',[cl.index("gx2raw"),cl.index("gy2raw"),cl.index("gz2raw")]],
            ['Mot Flags',[cl.index("MotFlags")]],
            ['Mot Pitch,Roll,Yaw',[cl.index("MotPitch"),cl.index("MotRoll"),cl.index("MotYaw")]],
            ['Vmax Pitch,Roll,Yaw',[cl.index("VmaxPitch"),cl.index("VmaxRoll"),cl.index("VmaxYaw")]],
            ['Vibe1',[cl.index("VibeX1"),cl.index("VibeY1"),cl.index("VibeZ1")]],
            ['Vibe2',[cl.index("VibeX2"),cl.index("VibeY2"),cl.index("VibeZ2")]] ]
        for entry in self.graphSelectorEntryList:
            self.addItemToGraphSelectorList( entry[0], False )
        self.wGraphSelectorList.item(1).setCheckState(QtCore.Qt.Checked)

        self.wGraphSelectorList.itemChanged.connect(self.updateGraphOnItemChanged)
        self.bGraphSelectorClear.clicked.connect(self.clearGraphSelection)
        self.bGraphShowPoints.clicked.connect(self.updateGraphOnItemChangedNoAutoRange)

        self.readSettings()

    def addItemToGraphSelectorList(self,name,check):
        item = QListWidgetItem()
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        if( check ):
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        item.setText(name)
        self.wGraphSelectorList.addItem(item)

    #slot for signal clicked from bGraphSelectorClear
    def clearGraphSelection(self,):
        for n in range(self.wGraphSelectorList.count()):
            self.wGraphSelectorList.item(n).setCheckState(QtCore.Qt.Unchecked)
        self.updateGraph()

    #slot for signal Load Log File, connection to signals in QTDesigner
    def loadLogFile(self):
        if self.loadLogThread.isRunning():
            return
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            'Load Data Logger file',
            self.fileDialogDir,
            '*.log;;All Files (*)'
            )
        if fileName:
            self.bLoad.setEnabled(False)
            self.actionLoad.setEnabled(False)
            self.bSave.setEnabled(False)
            self.actionSave.setEnabled(False)
            self.actionClear.setEnabled(False)
            self.wLogFileName.setText( fileName )
            self.wProgressBar.show()
            self.bCancelLoad.show()
            createTraffic = False
            if( self.bLoadTraffic.checkState()==QtCore.Qt.Checked ): createTraffic = True
            createPX4bin = True #this can be always true, doesn't take much time
            self.loadLogThread.setFile(fileName, createTraffic, createPX4bin)
            self.loadLogThread.start()

    #slot for signal progress of cLoadLogThread
    def loadLogFileProgress(self):
        self.wProgressBar.setValue(self.loadLogThread.progressValue)

    #slot for signal cancel of cLoadLogThread
    def loadLogFileCancel(self):
        self.loadLogThread.cancel()
        self.loadLogThread.clearUnrequired()
        self.wLogFileName.setText( self.currentLogFileName )
        self.wProgressBar.hide()
        self.bCancelLoad.hide()
        self.bLoad.setEnabled(True)
        self.actionLoad.setEnabled(True)
        self.bSave.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionClear.setEnabled(True)

    #slot for signal finished of cLoadLogThread
    def loadLogFileDone(self):
        if( self.loadLogThread.canceled ): return

        self.wProgressBar.setValue(10)
        if( self.loadLogThread.createTraffic ):
            self.wTrafficText.setPlainText( self.loadLogThread.traffic )
        else:
##            self.wTrafficText.setPlainText( "Traffic was not loaded.\nCheck >Load Traffic< and load file again." )
            self.wTrafficText.setPlainText( "Only first 500 commands were loaded.\n\n"+
                                             self.loadLogThread.traffic+"\n..." )
        self.wProgressBar.setValue(60)
        self.wDataText.setPlainText( self.loadLogThread.data )
        self.px4binlog = self.loadLogThread.px4bin
        self.wProgressBar.setValue(70)
        self.loadLogThread.clearUnrequired()
        self.currentLogFileName = self.loadLogThread.fileName

        self.bGraphShowPoints.setCheckState(QtCore.Qt.Unchecked)
##BUG: do a check here in case file is empty!!!
        try:
            self.nparraylog = np.loadtxt( StringIO(self.wDataText.toPlainText()), delimiter='\t', skiprows=2 )#, usecols=(0, 1) )
            self.nparraylog[:,0] *= 0.001
            self.nparraylog_initialized = True
        except:
            self.nparraylog_initialized = False
        self.wProgressBar.setValue(95)
        self.updateGraph()
        self.wProgressBar.setValue(100)

        self.wLogFileName.setText( self.currentLogFileName )
        self.wProgressBar.hide()
        self.bCancelLoad.hide()
        self.bLoad.setEnabled(True)
        self.actionLoad.setEnabled(True)
        self.bSave.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionClear.setEnabled(True)

    #slot for signal ClearLog File, connection to signals in QTDesigner
    def clearLogFile(self):
        self.wTrafficText.setPlainText( "" )
        self.wDataText.setPlainText( "" )
        self.loadLogThread.clearUnrequired()
        self.fileName = ''
        self.px4binlog = []
        self.nparraylog = ''
        self.nparraylog_initialized = False
        self.wGraphLegend.setText( '' )
        self.updateGraphCursor(0,0)
        self.pqPlotWidget.clear()
        self.wLogFileName.setText( self.fileName )
        self.bLoad.setEnabled(True)
        self.actionLoad.setEnabled(True)
        self.bSave.setEnabled(True)
        self.actionSave.setEnabled(False)
        self.actionClear.setEnabled(False)

    #slot for signal Save Into File, connection to signals in QTDesigner
    def saveDataIntoFile(self):
        if self.loadLogThread.isRunning():
            return
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            'Save Data to file',
            self.fileDialogDir,
            '*.dat;;*.txt;;*.csv;;PX4 .bin (*.bin)'
            )
        if fileName:
            if fileName.lower().endswith('.csv'):
                with open( fileName, 'w') as F:
                    F.write( self.wDataText.toPlainText().replace('\t',',') )
            elif fileName.lower().endswith('.bin'):
                with open( fileName, 'wb') as F:
                    for b in self.px4binlog: F.write(b)
            else:
                with open( fileName, 'w') as F:
                    F.write( self.wDataText.toPlainText() )


    #slot for signal itemChanged from wGraphSelectorList
    def updateGraphOnItemChanged(self,):
        self.updateGraph(False)

    #slot for signal clicked from bGraphShowPoints
    def updateGraphOnItemChangedNoAutoRange(self,):
        self.updateGraph(None)

    def updateGraph(self,doXYAutorange=True): #True: in xy, False: only in y, None: none
        if( not self.nparraylog_initialized ): return
        # get data colums to plot
##        with( pg.BusyCursor() ):
        indexes = []
        for n in range(self.wGraphSelectorList.count()):
            if( self.wGraphSelectorList.item(n).checkState() == QtCore.Qt.Checked ):
                indexes += self.graphSelectorEntryList[n][1]
        # clear
        self.pqPlotWidget.clear()
        self.pqPlotWidget.addItem(self.pgGraphTimeLine, ignoreBounds=True)
        # add selected plots
        x = self.nparraylog[:,0] #this is a view, i.e. not a duplicate
        nr = len(indexes)
        if( self.bGraphShowPoints.checkState()==QtCore.Qt.Checked ):
            for i in range(nr):
                self.pqPlotWidget.plot(x, self.nparraylog[:,indexes[i]],
                                       pen=(i,nr),
                                       symbol='o', symbolSize=4, symbolBrush=(i,nr), symbolPen=(i,nr) )
        else:
            for i in range(nr):
                self.pqPlotWidget.plot(x, self.nparraylog[:,indexes[i]], pen=(i,nr) )  ## setting pen=(i,3) automaticaly creates three different-colored pens
        # create label
        self.updateGraphLegend(indexes)
        # handle the time slider
        xRange = x[-1]/0.0015
        self.wGraphTimeSlider.setRange( 0, int(xRange) )
        self.wGraphTimeSlider.setSingleStep( 10 )
        self.wGraphTimeSlider.setPageStep( int(xRange/100.0) )
        # auto range as needed
        if( doXYAutorange==None ): return
        if( doXYAutorange ):
            self.pqPlotWidget.autoRange()
            #this is equal to
            # bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None) #is QRectF
            # if bounds is not None: self.pqPlotWidget.setRange(bounds, padding=None)
        else:
#COMMENT: it would be cooler if it would use the min/max for the given range
            bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None)
            if bounds is not None: self.pqPlotWidget.setYRange(bounds.bottom(), bounds.top())

    def updateGraphLegend(self, indexes):
        nr = len(indexes)
        label = ""
        for i in range(nr):
            col = pg.mkColor( (i,nr) )
            colstr = pg.colorStr(col)[:6]
            label += "<span style='color: #"+colstr+"'>"+self.logColumnList[indexes[i]] + "</span> , "
        self.wGraphLegend.setText( label[:-3] )


    def updateGraphCursor(self, x, y):
        self.wGraphCursor.setText( self.wGraphCursorFormatStr % (x,y))

    def updateGraphCursorEvent(self, event):
        #event is a QPointF
        if( self.pqPlotWidget.sceneBoundingRect().contains(event) ):
            mousePoint = self.pqPlotWidget.vb.mapSceneToView(event)
            self.updateGraphCursor( mousePoint.x(), mousePoint.y() )

    def updateGraphTimeLabel(self,time):
        if( time<0.0 ): time = 0.0
        if( time>4480.0 ): time = 4480.0
        qtimezero = QtCore.QTime(0,0,0,0)
        qtime = qtimezero.addMSecs(time*1000.0)
        self.wGraphTimeLabel.setText( self.wGraphTimeFormatStr % qtime.toString("mm:ss:zzz") )
        self.pgGraphTimeLine.setPos(time)

    def updateGraphTime(self,time):
        #self.updateGraphTimeLabel(time) #don't call this to avoid recursive call
        tindex = int(time/0.0015)
        if( tindex<0 ): tindex = 0
        if( tindex>self.wGraphTimeSlider.maximum() ): tindex = self.wGraphTimeSlider.maximum()
        self.wGraphTimeSlider.setValue( tindex ) #this emits also a updateGraphTimeSliderValueChangedEvent

    def updateGraphRangeChangedEvent(self,event):
        xRange = event.viewRange()[0]
        time = 0.5*( xRange[0] + xRange[1] )
        self.updateGraphTime(time)

    def updateGraphTimeSliderValueChangedEvent(self,event):
        time = float(event)*0.0015
        xRange = self.pqPlotWidget.viewRange()[0]
        deltatime = 0.5*( xRange[1] - xRange[0] )
        self.pqPlotWidget.setXRange( time-deltatime, time+deltatime, padding=0.0 )
        self.updateGraphTimeLabel(time)

    def doGraphZoomFactor(self):
        xRange = self.pqPlotWidget.viewRange()[0]
        #print( xRange )
        time = 0.5*( xRange[0] + xRange[1] )
        bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None) #is QRectF
        #print( bounds )
        #index = self.wGraphZoomFactor.currentIndex() #['1 x','1/10 x','1/100 x','10 s','5 s','1 s','100 ms']
        index = self.wGraphZoomFactor.currentText() #['100 %','10 %','1 %','10 s','5 s','1 s','100 ms']
        print( index )
        if( index=='100 %' ):    deltatime = 0.5*( bounds.right() - bounds.left() )
        elif( index=='10 %' ):   deltatime = 0.05*( bounds.right() - bounds.left() )
        elif( index=='1 %' ):    deltatime = 0.005*( bounds.right() - bounds.left() )
        elif( index=='30 s' ):   deltatime = 15.0
        elif( index=='10 s' ):   deltatime = 5.0
        elif( index=='5 s' ):    deltatime = 2.5
        elif( index=='2 s' ):    deltatime = 1.0
        elif( index=='1 s' ):    deltatime = 0.5
        elif( index=='100 ms' ): deltatime = 0.05
        self.pqPlotWidget.setXRange( time-deltatime, time+deltatime, padding=0.0 )
        self.updateGraphTimeLabel(time)


    #slot for signal openAbout, connection to signals in QTDesigner
    def openAbout(self):
        QMessageBox.about(self, 'NT DataLogger Tool About',
            "OlliW's NT DataLogger Tool\n\n" +
            "(c) OlliW @ www.olliw.eu\n\n"+VersionStr+"\n\n" +
            "This program is part of the STorM32 gimbal controller project.    \n" +
            "Project web page: http://www.olliw.eu/\n\n"
            )

    def readSettings(self):
        settings = QSettings(IniFileStr, QSettings.IniFormat)
        if( int(settings.value('SYSTEM/LoadTraffic',0)) ):
            self.bLoadTraffic.setCheckState(QtCore.Qt.Checked)
        #if( int(settings.value('SYSTEM/GraphShowPoints',0)) ):
        #    self.bGraphShowPoints.setCheckState(QtCore.Qt.Checked)

    def writeSettings(self):
        settings = QSettings(IniFileStr, QSettings.IniFormat)
        if( self.bLoadTraffic.checkState()==QtCore.Qt.Checked ):
            settings.setValue('SYSTEM/LoadTraffic',1)
        else:
            settings.setValue('SYSTEM/LoadTraffic',0)
        if( self.bGraphShowPoints.checkState()==QtCore.Qt.Checked ):
            settings.setValue('SYSTEM/GraphShowPoints',1)
        else:
            settings.setValue('SYSTEM/GraphShowPoints',0)
        settings.setValue('SYSTEM/Style',appPalette)
        settings.sync()

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()




###################################################################
# Main()
##################################################################
if __name__ == '__main__':

    # as first step set the device pixel ratio, is either 1.0 or 2.0
    #  this is required to make other packages as happy as possible, e.g. pyqtgraph and QMessageBox
    from win32api import GetSystemMetrics   #see also: https://msdn.microsoft.com/en-us/library/windows/desktop/ms724385%28v=vs.85%29.aspx
    winScaledYRes = GetSystemMetrics(1) #returns the diplsay resolution = SM_CYSCREEN
    from ctypes import windll
    dc = windll.user32.GetDC(0)
    winYRes = windll.gdi32.GetDeviceCaps(dc,117) #= DESKTOPVERTRES, see https://msdn.microsoft.com/de-de/library/windows/desktop/dd144877%28v=vs.85%29.aspx
    winScale1 = float(winYRes)/float(winScaledYRes)
    winScaleEnvironment = int(winScale1)
    import os  #os.environment is effective only when called before app is v?created
    os.environ['QT_DEVICE_PIXEL_RATIO'] = str(winScaleEnvironment) #this soehow only takes/allows integer values!!!

    app = QApplication(sys.argv)

    settings = QSettings(IniFileStr, QSettings.IniFormat)
    appPalette = settings.value('SYSTEM/Style','Standard')
    if( appPalette == 'Fusion' ):
        QApplication.setStyle(QStyleFactory.create('Fusion'))
    else:
        appPalette = 'Standard'
        QApplication.setPalette(QApplication.style().standardPalette())

    # as second step set the WINSCALE
    #  do this by determining the "real" Windows scale form the fonts, and then corricting for the previously set scale
    #  ratio = app.primaryScreen().devicePixelRatio() #works, gives 1.0 or 2.0
    #  ratio = app.devicePixelRatio() #works, gives 1.0 or 2.0
    winScale = 1.0
    winScaleFont = ( 3.0 * QFontInfo(app.font()).pixelSize() )/( 4.0 * QFontInfo(app.font()).pointSizeF() )
    winScale = float(winScaleFont)/float(winScaleEnvironment)
    if( winScale<1.0 ): winScale = 1.0

    main = cMain(winScale, appPalette)
    main.show()
    sysexit = app.exec_()
    sys.exit(sysexit)




#QApplication.processEvents()
#QtGui.qApp.processEvents()

#    QApplication.setStyle(QStyleFactory.create('Windows'))
#    QApplication.setStyle(QStyleFactory.create('Fusion'))
#    QApplication.setPalette(QApplication.style().standardPalette())
#    QApplication.setPalette(QApplication.palette())

#https://www.snip2code.com/Snippet/683053/Qt5-Fusion-style-%28dark-color-palette%29
#qApp->setStyle(QStyleFactory::create("fusion"));
#QPalette palette;
#palette.setColor(QPalette::Window, QColor(53,53,53));
#palette.setColor(QPalette::WindowText, Qt::white);
#palette.setColor(QPalette::Base, QColor(15,15,15));
#palette.setColor(QPalette::AlternateBase, QColor(53,53,53));
#palette.setColor(QPalette::ToolTipBase, Qt::white);
#palette.setColor(QPalette::ToolTipText, Qt::white);
#palette.setColor(QPalette::Text, Qt::white);
#palette.setColor(QPalette::Button, QColor(53,53,53));
#palette.setColor(QPalette::ButtonText, Qt::white);
#palette.setColor(QPalette::BrightText, Qt::red);
#palette.setColor(QPalette::Highlight, QColor(142,45,197).lighter());
#palette.setColor(QPalette::HighlightedText, Qt::black);
#qApp->setPalette(palette);


#https://gist.github.com/lschmierer/443b8e21ad93e2a2d7eb
#qApp.setStyle("Fusion")
#dark_palette = QPalette()
#dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
#dark_palette.setColor(QPalette.WindowText, Qt.white)
#dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
#dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
#dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
#dark_palette.setColor(QPalette.ToolTipText, Qt.white)
#dark_palette.setColor(QPalette.Text, Qt.white)
#dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
#dark_palette.setColor(QPalette.ButtonText, Qt.white)
#dark_palette.setColor(QPalette.BrightText, Qt.red)
#dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
#dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
#dark_palette.setColor(QPalette.HighlightedText, Qt.black)
#qApp.setPalette(dark_palette)
#qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    '''
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
#    form.setPalette(dark_palette)
    QApplication.setPalette(dark_palette)
    '''

#DevicePixelRatio experiments
'''
ratio = QApplication.primaryScreen().devicePixelRatio()

=> gives always 1.0, independent on Win Scaling
'''

#FONT sizes experiments
'''
str(QFontInfo(appfont).pixelSize()) + ","+
str(QFontInfo(appfont).pointSize()) + ","+
str(QFontInfo(appfont).pointSizeF()) +"\n"+

str(QFontInfo(self.wTab.font()).pixelSize()) + ","+
str(QFontInfo(self.wTab.font()).pointSize()) + ","+
str(QFontInfo(self.wTab.font()).pointSizeF()) +"\n"+

str(QFontInfo(self.wDataText.font()).pixelSize()) + ","+
str(QFontInfo(self.wDataText.font()).pointSize()) + ","+
str(QFontInfo(self.wDataText.font()).pointSizeF())

Win Scaling 100%:
11  8   8.25
11  8   8.25
13  10  9.75
Win Scaling 150%:
13  8   7.8
13  8   7.8
17  10  10.2
Win Scaling 150%:
16  8   8.0
16  8   8.0
20  10  10.0
Win Scaling 200%:
21  8   7.875
21  8   7.875
27  10  10.125
Win Scaling 250%:
27  8   8.1
27  8   8.1
33  10  9.9

=> pixelSize = pointSizeF * 4/3 * WinScaling

=> SCALE = ( 3 * pixelSize )/( 4 * pointSizeF )
'''

'''
    from win32api import GetSystemMetrics   #see also: https://msdn.microsoft.com/en-us/library/windows/desktop/ms724385%28v=vs.85%29.aspx
    winScaledYRes = GetSystemMetrics(1) #returns the diplsay resolution = SM_CYSCREEN
    from ctypes import windll
    dc = windll.user32.GetDC(0)
    winYRes = windll.gdi32.GetDeviceCaps(dc,117) #= DESKTOPVERTRES, see https://msdn.microsoft.com/de-de/library/windows/desktop/dd144877%28v=vs.85%29.aspx
    winScale1 = float(winYRes)/float(winScaledYRes)
    winScaleEnvironment = int(winScale1)
    import os  #os.environment is effective only when called before app is v?created
    os.environ['QT_DEVICE_PIXEL_RATIO'] = str(winScaleEnvironment) #this soehow only takes/allows integer values!!!

    This worked for all except 125%!
    winScale = str(winYRes) + "," + str(winScaledYRes) + "="+str( float(winYRes)/float(winScaledYRes) ) + "!"
    100%    1800,1800=1.0
    125%    1800,1800=1.0
    150%    1800,1200=1.5
    200%    1800,900=2.0
    250%    1800,720=2.5
    '''



#        QMessageBox msgBox
#        msgBox.setText("The document has been modified.")
#        msgBox.setInformativeText("Do you want to save your changes?")
#        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
#        msgBox.setDefaultButton(QMessageBox.Save)
#        ret = msgBox.exec_()
#        reply = QMessageBox.question(self, 'Message',
#            "Are you sure to quit?", QMessageBox.Ok, QMessageBox.Ok)
