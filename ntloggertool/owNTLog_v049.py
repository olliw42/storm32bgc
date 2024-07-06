# Version v0.49 30. July 2022

###############################################################################
# cNTLogDataItemList
# class to store nt data columns
#-----------------------------------------------------------------------------#
# is needed here since cNTLogFileReader needs a list to generate the header in the datalog

###############################################################################
# cNTLogDataFrame
# this is the class to handle and host the data of one frame
#-----------------------------------------------------------------------------#

#this is a base class for handling NT log data
#class cNTLogDataFrameBase:

#this is a child class for handling NT log data
#class cNTLogDataFrame(cNTLogDataFrameBase):

#this is a child class for handling NT serial data streams
#class cNTLogSerialDataFrame(cNTLogDataFrame):

###############################################################################
# cNTLogParser
# this is the main class to parse a stream of log packets into a cNTLogDataFrame
#-----------------------------------------------------------------------------#

###############################################################################
# cNTLogFileReader
# this is the main class to read in a NTLogger data log file
# it generates a number of data lists, for easier handling in the GUI
#-----------------------------------------------------------------------------#


import struct
from datetime import datetime
from math import sqrt, sin, cos, pi, atan2
from PyQt5.QtCore import QFile
from owNTLoggerObjects_v042 import * #cLogDataItemList


##defined alreadycNTLOGVERSION_UNINITIALIZED = 0
cLOGVERSION_NT_V2 = 2 #new V2 commands
cLOGVERSION_NT_V3 = 3 #SetLog extended to 0.001?
cLOGVERSION_NT_LATEST = 3 #this is an alias to the latest version

#!!!!! IT WILL CRASH IF VERSION IS NOT V3 !!!!!

###############################################################################
# cNTLogDataItemList
# class to store nt data columns
#-----------------------------------------------------------------------------#
# is needed here since cNTLogFileReader needs a list to generate the header in the datalog
# the list must be compatible in sequence to the list used by cLogItemList in the main
class cNTLogDataItemList(cLogDataItemList):

    #this is a human-readable list of how to organize the standard NTLogger data field names into catagories
    #is used in getGraphSelectorList()

    def __init__(self,_translator=None):
        super().__init__(_translator)
        self.setToStandardNTLoggerItemList()
        self.setToStandardNTLoggerGraphSelectorList()

    #the order of the main items can be as we want it to be
    #the order of the sub items within a main item is given by the order in setToStandardNTLoggerItemList()
    def setToStandardNTLoggerGraphSelectorList(self):
        self.graphSelectorList = [
        ['Performance',["Imu1rx","Imu1done","PIDdone","Motdone","Imu2rx","Imu2done","Logdone","Loopdone"]],
        ['Imu1 Pitch,Roll,Yaw',["Imu1Pitch","Imu1Roll","Imu1Yaw"]],
        ['Imu2 Pitch,Roll,Yaw',["Imu2Pitch","Imu2Roll","Imu2Yaw"]],
        ['Encoder Pitch,Roll,Yaw',["EncPitch*","EncRoll*","EncYaw*"]], #injected, converted to angles
        ['PID Error Pitch,Roll,Yaw',["PIDErrorPitch","PIDErrorRoll","PIDErrorYaw"]],
        ['PID SetP Pitch,Roll,Yaw',["PIDEffSetPointPitch*","PIDEffSetPointRoll*","PIDEffSetPointYaw*", #injected
                                    "PIDSetPointPitch","PIDSetPointRoll","PIDSetPointYaw",
                                    "PIDPanSetPointPitch*","PIDPanSetPointRoll*","PIDPanSetPointYaw*"]], #injected
        ['PID P I D Pitch,Roll,Yaw',["PPitch*","PRoll*","PYaw*", #injected
                                     "IPitch","IRoll","IYaw",
                                     "DPitch","DRoll","DYaw",
                                     "IPitch*","IRoll*","IYaw*", #injected
                                     "DPitch*","DRoll*","DYaw*"]], #injected
#        ['PID Pitch,Roll,Yaw',["PIDPitch","PIDRoll","PIDYaw"]],
#        ['PID Mot Pitch,Roll,Yaw',["PIDMotPitch","PIDMotRoll","PIDMotYaw"]],
        ['PID Pitch,Roll,Yaw',["PIDPitch","PIDRoll","PIDYaw","PIDMotPitch","PIDMotRoll","PIDMotYaw"]],
        ['Ahrs1',["Rx1","Ry1","Rz1","AccAmp1*","AccConf1","YawTarget"]],  #AccAmp1 is injected
#        ['State',['State','Status','Status2','ErrorCnt']],
        ['State',['State']],
        ['Error',['ErrorCnt']],
        ['Voltage',['Voltage']],
        ['STorM32 Link',["q0","q1","q2","q3","vx","vy","vz","YawRateCmd","FCStatus","SLStatus",
                         "FailsafeCnt","A1ValidFailCnt","received"]], #STL
        ['Acc1',["ax1","ay1","az1"]],
        ['Gyro1',["gx1","gy1","gz1"]],
        ['Acc2',["ax2","ay2","az2"]],
        ['Gyro2',["gx2","gy2","gz2"]],
        ['Sensor States',["Imu1State","Imu2State","MotState"]],
        ['Acc1 raw',["ax1raw","ay1raw","az1raw"]],
        ['Gyro1 raw',["gx1raw","gy1raw","gz1raw"]],
        ['Acc2 raw',["ax2raw","ay2raw","az2raw"]],
        ['Gyro2 raw',["gx2raw","gy2raw","gz2raw"]],
        ['Temp 1+2',["T1","T2"]],
        ['Mot Flags',["MotFlags"]],
        ['Mot Pitch,Roll,Yaw',["MotPitch","MotRoll","MotYaw"]],
        ['Vmax Pitch,Roll,Yaw',["VmaxPitch","VmaxRoll","VmaxYaw"]],
        ['dU Pitch,Roll,Yaw',["dUPitch*","dURoll*","dUYaw*"]], #injected, converted to angles
        ['Encoder raw',["EncRawPitch","EncRawRoll","EncRawYaw"]],
        ['dU raw',["dURawPitch","dURawRoll","dURawYaw"]],
        ['Inputs',['InputPitch','InputRoll','InputYaw','InputPanMode','InputStandBy','InputCamera',
                   'InputReCenterCamera','InputScript1','InputScript2','InputScript3','InputScript4',
                   'InputPwmOut','InputCamera2']],
        ['Camera',["CameraModel","CameraCmd","CameraValue","CameraPwm","CameraCmd2","CameraValue2"]],
        ['Debug',["debug1","debug2","debug3","debug4","debug5","debug6","debug7","inj1*","inj2*","inj3*"]], #STL
        ]

    #the list order must be identical to that in class cNTLogFileReader, getDataLine() !!!!
    #keeps information which is used for the various data formats
    def setToStandardNTLoggerItemList(self):
        self.clear()
        self.addItem( 'Time', 'ms', cDATATYPE_U64, cDATATYPE_FLOAT )
        self.addItem( 'Imu1rx', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Imu1done', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'PIDdone', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Motdone', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Imu2rx', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Imu2done', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Logdone', 'us', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'Loopdone', 'us', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'State', 'uint', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'Status', 'hex', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'Status2', 'hex', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'ErrorCnt', 'uint', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'Voltage', 'V', cDATATYPE_U16, cDATATYPE_FLOAT )

        self.addItem( 'ax1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'ay1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'az1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gx1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gy1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gz1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'Imu1State', 'hex', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'ax2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'ay2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'az2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gx2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gy2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gz2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'Imu2State', 'hex', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'Imu1Pitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Imu1Roll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Imu1Yaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Imu2Pitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Imu2Roll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Imu2Yaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )

        self.addItem( 'EncPitch*', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'EncRoll*', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'EncYaw*', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value

        self.addItem( 'MotState', 'hex', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'PIDErrorPitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDErrorRoll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDErrorYaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDEffSetPointPitch*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PIDEffSetPointRoll*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PIDEffSetPointYaw*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PIDSetPointPitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDSetPointRoll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDSetPointYaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDPanSetPointPitch*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PIDPanSetPointRoll*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PIDPanSetPointYaw*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value

        self.addItem( 'PPitch*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PRoll*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'PYaw*', 'deg', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'IPitch', 'deg*S', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'IRoll', 'deg*S', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'IYaw', 'deg*s', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'DPitch', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'DRoll', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'DYaw', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT )
        self.addItem( 'IPitch*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'IRoll*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'IYaw*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'DPitch*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'DRoll*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'DYaw*', 'deg/s', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value

        self.addItem( 'PIDPitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDRoll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDYaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDMotPitch', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDMotRoll', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'PIDMotYaw', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )

        self.addItem( 'Rx1', 'g', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Ry1', 'g', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'Rz1', 'g', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'AccAmp1*', 'g', cDATATYPE_Ux, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'AccConf1', 'uint', cDATATYPE_U16, cDATATYPE_FLOAT )
        self.addItem( 'YawTarget', 'deg', cDATATYPE_S16, cDATATYPE_FLOAT )

        self.addItem( 'MotFlags', 'hex', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'VmaxPitch', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'MotPitch', 'uint', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'VmaxRoll', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'MotRoll', 'uint', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'VmaxYaw', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'MotYaw', 'uint', cDATATYPE_U16, cDATATYPE_Ux )

        self.addItem( 'dUPitch*', '', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'dURoll*', '', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'dUYaw*', '', cDATATYPE_S16, cDATATYPE_FLOAT ) #injected value

        self.addItem( 'q0', '', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'q1', '', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'q2', '', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'q3', '', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'vx', 'm/s', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'vy', 'm/s', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'vz', 'm/s', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'YawRateCmd', 'int', cDATATYPE_S16, cDATATYPE_FLOAT )
        self.addItem( 'FCStatus', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'SLStatus', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'FailsafeCnt', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'A1ValidFailCnt', 'uint', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'received', 'uint', cDATATYPE_U8, cDATATYPE_Ux )

        self.addItem( 'ax1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'ay1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'az1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gx1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gy1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gz1raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'T1', 'o', cDATATYPE_S16, cDATATYPE_FLOAT )

        self.addItem( 'ax2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'ay2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'az2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gx2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gy2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'gz2raw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'T2', 'o', cDATATYPE_S16, cDATATYPE_FLOAT )

        self.addItem( 'EncRawPitch', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'EncRawRoll', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'EncRawYaw', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'dURawPitch', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'dURawRoll', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'dURawYaw', 'int', cDATATYPE_S16, cDATATYPE_Sx )

        self.addItem( 'CameraModel', 'int', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'CameraCmd', 'int', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'CameraValue', 'int', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'CameraPwm', 'int', cDATATYPE_U16, cDATATYPE_Ux )
        self.addItem( 'CameraCmd2', 'int', cDATATYPE_U8, cDATATYPE_Ux )
        self.addItem( 'CameraValue2', 'int', cDATATYPE_U16, cDATATYPE_Ux )

        self.addItem( 'InputPitch', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputRoll', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputYaw', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputPanMode', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputStandBy', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputCamera', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputReCenterCamera', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputScript1', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputScript2', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputScript3', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputScript4', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputPwmOut', 'int', cDATATYPE_S8, cDATATYPE_Sx )
        self.addItem( 'InputCamera2', 'int', cDATATYPE_S8, cDATATYPE_Sx )

        self.addItem( 'debug1', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug2', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug3', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug4', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug5', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug6', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'debug7', 'int', cDATATYPE_S16, cDATATYPE_Sx )
        self.addItem( 'inj1*', '', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'inj2*', '', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value
        self.addItem( 'inj3*', '', cDATATYPE_Sx, cDATATYPE_FLOAT ) #injected value

    #self.graphSelectorList may be a larger list than that generated by getGraphSelectorList()
    def getGraphSelectorDefaultIndex(self, graphSelectorList=None): #allows to check in a modified list
        if not graphSelectorList: 
            graphSelectorList = self.graphSelectorList
        for i in range(len(graphSelectorList)):
            if graphSelectorList[i][0] == 'Imu1 Pitch,Roll,Yaw': return i
        for i in range(len(graphSelectorList)):
            if graphSelectorList[i][0] == 'Acc1': return i
        return None

    def getIndexByName(self, name, graphSelectorList=None):
        for i in range(len(self.list)):
            if self.list[i]['name'] == name: return self.list[i]['index']
            #if graphSelectorList[i]['name'] == name: return graphSelectorList[i]['index']
        return None


###############################################################################
# cNTLogDataFrame
# this is the base class to handle and host the data of one frame
# a frame is all data send in one cycle, i.e. from TRG ALL to next TRG ALL
# it just provides a skeleton, for holding the data and generating data text lines
# the actual decoding is implemented in a child class
#-----------------------------------------------------------------------------#
# Note: The data on the NTBus is in a different format than the data in the NT log file
# A) On the NTBus, most packets are send using the default send function, which uses the highbits mechanism
# to handle the 7th bit
# some packets have their own 7th bit handling, specifically:
# - setmotoralldata/setmotoralldataVFoc
# - setcameradata/setcameradata2
# B) Some packets have a special encoding of some values, which the NTLogger decodes, specifically:
# - tNTBusSetLoggerDataV3 (has highres fields)
# - tNTBusCmdPidInData (has highres fields)
# - tNTBusSetCameraData (has shifted values to allow for 0 = ignore)
#-----------------------------------------------------------------------------#
# NTLogger decodes the data on the NT bus and stores that decoded data on the SD card
# error handling:
#   there are two types of error, (i) a package is incomplete, (ii) a crucial package is not complete
#   self.error is set, depending on the general error type
#   each doXXX returns True or False, so that a parser can determine more detailed error conditions

#these error flags are used only by the serial data frame
cNTDATAFRAME_OK = 0
cNTDATAFRAME_CMDERROR = 1
cNTDATAFRAME_SETMOTERROR = 2
cNTDATAFRAME_SETLOGERROR = 4

cNTBUS_MOTOR_FLAG_FOC = 0x20 #is needed to distinguish "non-encoder" and "encoder" versions of SetMotAll
cNTBUS_CAMERA_FLAG_SET2 = 0x40 #this is to map two data into SET


#this is a base class
# it holds all data, and provides convenience functions to set them, and extract them as dataline and rawline
class cNTLogDataFrameBase:

    def __init__(self):
        self.logVersion = cLOGVERSION_NT_LATEST #allows to detect different log file versions, latest version as default
        self.Time = 0 #that's the actual time of a data frame

        self.clear()

        #injected values
        self.Time = self.TimeStamp32
        self.fAhrs1AccAmp_inj = 0.0
        self.PIDEffSetPointPitch_inj = self.PIDEffSetPointRoll_inj = self.PIDEffSetPointYaw_inj = 0
        self.PIDPanSetPointPitch_inj = self.PIDPanSetPointRoll_inj = self.PIDPanSetPointYaw_inj = 0
        self.PIDPPitch_inj = self.PIDPRoll_inj = self.PIDPYaw_inj = 0
        self.PIDIPitch_inj = self.PIDIRoll_inj = self.PIDIYaw_inj = 0
        self.PIDDPitch_inj = self.PIDDRoll_inj = self.PIDDYaw_inj = 0
        self.PIDDPitch_inj_last = self.PIDDRoll_inj_last = self.PIDDYaw_inj_last = 0
        self.EncAnglePitch_inj = self.EncAngleRoll_inj = self.EncAngleYaw_inj = 0 #this is converted to deg
        self.dUPitch_inj = self.dURoll_inj = self.dUYaw = 0 #this is converted to 1
        self.dbg_inj1 = self.dbg_inj2 = self.dbg_inj3 = 0

        self.t_last = 0
        self.vn_x = self.vn_y = self.vn_z = 0
        self.an_x = self.an_y = self.an_z = 0

        self.vx_last = self.vy_last = self.vz_last = 0

    def setLogVersion(self,ver):
        self.logVersion = ver

    def getLogVersion(self):
        return self.logVersion

    def clear(self):
        #tNTBusSetLoggerDataV3
        self.TimeStamp32 = 0
        self.Imu1received,self.Imu1done,self.PIDdone,self.Motorsdone  = 0,0,0,0
        self.Imu2received,self.Imu2done,self.Logdone,self.Loopdone = 0,0,0,0
        self.State,self.Status,self.Status2,self.ErrorCnt,self.Voltage = 0,0,0,0,0
        self.Imu1AnglePitch,self.Imu1AngleRoll,self.Imu1AngleYaw = 0,0,0
        self.Imu2AnglePitch,self.Imu2AngleRoll,self.Imu2AngleYaw = 0,0,0
        self.SetLoggerData_received = 0

        #tNTBusCmdEncoderData
        self.EncRawPitch,self.EncRawRoll,self.EncRawYaw,self.MotState = 0,0,0,0 #this is the received, raw data
        self.CmdEncoderData_received = 0

        #tNTBusSetMotorAllData, tNTBusSetMotorAllDataVFoc
        self.Flags,self.VmaxPitch,self.MotPitch,self.VmaxRoll,self.MotRoll,self.VmaxYaw,self.MotYaw = 0,0,0,0,0,0,0
        self.dURawPitch,self.dURawRoll,self.dURawYaw = 0,0,0  #this is the received, raw data
        self.SetMotorAllData_received = 0

        #tNTBusSetCameraData, tNTBusSetCameraData2
        self.CameraFlags,self.CameraModel,self.CameraCmd,self.CameraValue,self.CameraPwm = 0,0,0,0,0
        self.CameraCmd2,self.CameraValue2 = 0,0
        self.SetCameraData_received = 0

        #tNTBusCmdStorm32LinkDataV2
        self.q0,self.q1,self.q2,self.q3 = 0,0,0,0
        self.vx,self.vy,self.vz = 0,0,0
        self.YawRateCmd,self.SLFCStatus,self.SLStatus = 0,0,0
        self.Storm32LinkFailsafeCnt,self.A1ValidFailCnt = 0,0
        self.CmdStorm32LinkData_received = 0

        #tNTBusCmdAccGyroDataV2
        self.ax1,self.ay1,self.az1,self.gx1,self.gy1,self.gz1,self.Imu1State = 0,0,0,0,0,0,0
        self.ax2,self.ay2,self.az2,self.gx2,self.gy2,self.gz2,self.Imu2State = 0,0,0,0,0,0,0
        self.CmdAccGyro1Data_received = 0
        self.CmdAccGyro2Data_received = 0

        #tNTBusCmdAccGyroRawDataV2
        self.ax1raw,self.ay1raw,self.az1raw,self.gx1raw,self.gy1raw,self.gz1raw,self.temp1 = 0,0,0,0,0,0,0
        self.ax2raw,self.ay2raw,self.az2raw,self.gx2raw,self.gy2raw,self.gz2raw,self.temp2 = 0,0,0,0,0,0,0
        self.CmdAccGyro1RawData_received = 0
        self.CmdAccGyro2RawData_received = 0

        #tNTBusCmdPidInData, tNTBusCmdPidIDData, tNTBusCmdPidData
        self.PIDErrorPitch,self.PIDErrorRoll,self.PIDErrorYaw = 0,0,0
        self.PIDSetPointPitch,self.PIDSetPointRoll,self.PIDSetPointYaw = 0,0,0
        self.PIDIPitch, self.PIDIRoll, self.PIDIYaw = 0,0,0
        self.PIDDPitch, self.PIDDRoll, self.PIDDYaw = 0,0,0
        self.PIDCntrlPitch,self.PIDCntrlRoll,self.PIDCntrlYaw = 0,0,0
        self.PIDMotorCntrlPitch,self.PIDMotorCntrlRoll,self.PIDMotorCntrlYaw = 0,0,0
        self.CmdPidInData_received = 0
        self.CmdPidIDData_received = 0
        self.CmdPidOutData_received = 0

        #tNTBusCmdAhrsData
        self.Ahrs1Rx,self.Ahrs1Ry,self.Ahrs1Rz,self.Ahrs1AccConfidence,self.Ahrs1YawTarget = 0,0,0,0,0
        self.Ahrs2Rx,self.Ahrs2Ry,self.Ahrs2Rz,self.Ahrs2AccConfidence,self.Ahrs2YawTarget = 0,0,0,0,0
        self.CmdAhrs1Data_received = 0
        self.CmdAhrs2Data_received = 0

        #tNTBusCmdDebugData
        self.debug1,self.debug2,self.debug3,self.debug4,self.debug5,self.debug6,self.debug7 = 0,0,0,0,0,0,0
        self.CmdDebugData_received = 0

        #tNTBusCmdTunnelTx
        self.TunnelTxLen = 0
        self.TunnelTxData = []
        self.CmdTunnelTx_received = 0

        #tNTBusCmdWriteLoggerDateTime
        self.RtcYear,self.RtcMonth,self.RtcDay,self.RtcHour,self.RtcMinute,self.RtcSecond = 0,0,0,0,0,0
        self.CmdWriteLoggerDateTime_received = 0

        #tNTBusCmdAutopilotSystemTime
        self.UnixTime = 0
        self.CmdAutopilotSystemTime_received = 0

        #tNTBusCmdFunctionInputValues
        self.InputPitch = self.InputRoll = self.InputYaw = 0
        self.InputPanMode = 0
        self.InputStandBy = 0
        self.InputCamera = 0
        self.InputReCenterCamera = 0
        self.InputScript1 = self.InputScript2 = self.InputScript3 = self.InputScript4 = 0
        self.InputPwmOut = 0
        self.InputCamera2 = 0
        self.CmdFunctionInputValues_received = 0

        self.error = cNTDATAFRAME_OK #new frame, new game

    #some default functions to set values
    def setLogger_V3(self,tupel):
        (self.TimeStamp32,
         self.Imu1received,self.Imu1done,self.PIDdone,self.Motorsdone,
         self.Imu2done,self.Logdone,self.Loopdone,
         self.State,self.Status,self.Status2,self.ErrorCnt,self.Voltage,
         self.Imu1AnglePitch,self.Imu1AngleRoll,self.Imu1AngleYaw,
         self.Imu2AnglePitch,self.Imu2AngleRoll,self.Imu2AngleYaw,
        ) = tupel
    ''' 
    there are no further setters for setting the varied data fields
    as it can happen that a payload doesn't have exactly the tuple structure
    so we do set the fields explicitly in the parent class
    '''     
    
    #some default prototypes, are all called by parser
    def doSetLogger(self,payload): return True
    def doSetMotorAll(self,payload): return True
    def doSetMotorAllVFoc(self,payload): return True
    def doSetCamera(self,payload): return True
    def doSetCamera2(self,payload): return True
    def doCmdAccGyro1_V2(self,payload): return True
    def doCmdAccGyro2_V2(self,payload): return True
    def doCmdAccGyro1Raw_V2(self,payload): return True
    def doCmdAccGyro2Raw_V2(self,payload): return True
    def doCmdEncoder(self,payload): return True
    def doCmdPidIn(self,payload): return True
    def doCmdPidID(self,payload): return True
    def doCmdPidOut(self,payload): return True
    def doCmdAhrs1(self,payload): return True
    def doCmdAhrs2(self,payload): return True
    def doCmdStorm32LinkData(self,payload): return True
    def doCmdStorm32LinkData_V2(self,payload): return True
    def doCmdDebugData(self,payload): return True
    def doCmdParameter(self,payload): return True
    def doCmdTunnelTx(self,payload): return True
    def doCmdWriteLoggerDateTime(self,payload): return True
    def doCmdAutopilotSystemTime(self,payload): return True
    def doCmdFunctionInputValues(self,payload): return True

    #default prototype, is called by parser
    def readCmdByte(self): return 255

    #default prototype, is called by serial reader thread
    def isValid(self): return True

    def calculateTime(self,datalog_TimeStamp32_start):
        self.Time = self.TimeStamp32 - datalog_TimeStamp32_start

    def calculateInjectedValues(self):
        self.fAhrs1AccAmp_inj = sqrt(self.ax1*self.ax1 + self.ay1*self.ay1 + self.az1*self.az1)*10000.0/8192.0

        self.EncAnglePitch_inj = self.EncRawPitch * 360.0 / 65536.0 #raw is int16
        self.EncAngleRoll_inj = self.EncRawRoll * 360.0 / 65536.0 #raw is int16
        self.EncAngleYaw_inj = self.EncRawYaw * 360.0 / 65536.0 #raw is int16

        self.dUPitch_inj = self.dURawPitch / 65536.0 #raw is q16
        self.dURoll_inj = self.dURawRoll / 65536.0 #raw is q16
        self.dUYaw_inj = self.dURawYaw / 65536.0 #raw is q16

        #Error = EffectiveSetpoint - Angle = Setpoint - PanSetPoint - Angle
        #I've tested it, except before NORMAL state is reached, this indeed coincides with cpid->EffectiveSetPoint
        #Angle is in 0.001 deg
        #Error is in 0.001 deg
        #SetPoint is in 0.01 deg
        self.PIDEffSetPointPitch_inj = self.PIDErrorPitch + self.Imu1AnglePitch # is in 0.001 deg
        self.PIDEffSetPointRoll_inj = self.PIDErrorRoll + self.Imu1AngleRoll
        self.PIDEffSetPointYaw_inj = self.PIDErrorYaw + self.Imu1AngleYaw

        #we take the negative of it, so it can be better compared to Angle
        self.PIDPanSetPointPitch_inj = -(self.PIDSetPointPitch - 0.1*self.PIDEffSetPointPitch_inj) # is in 0.01 deg
        self.PIDPanSetPointRoll_inj = -(self.PIDSetPointRoll - 0.1*self.PIDEffSetPointRoll_inj)
        self.PIDPanSetPointYaw_inj = -(self.PIDSetPointYaw - 0.1*self.PIDEffSetPointYaw_inj)

        #PID P = P*Error
        self.PIDPPitch_inj = self.PIDErrorPitch # is in 0.001 deg # differs by P
        self.PIDPRoll_inj = self.PIDErrorRoll
        self.PIDPYaw_inj = self.PIDErrorYaw
        #PID I = I*integral Error dt
        self.PIDIPitch_inj = self.PIDIPitch_inj + self.PIDErrorPitch # is in 0.001 * 0.0015 deg*s # differs by I*dt with dt in ms
        self.PIDIRoll_inj = self.PIDIRoll_inj + self.PIDErrorRoll
        self.PIDIYaw_inj = self.PIDIYaw_inj + self.PIDErrorYaw
        #PID D = D * d/dt (-Angle)
        self.PIDDPitch_inj = ((-self.Imu1AnglePitch) - self.PIDDPitch_inj_last) # is in 0.001 / 0.0015 deg/s # differs by D/dt with dt in ms
        self.PIDDRoll_inj = ((-self.Imu1AngleRoll) - self.PIDDRoll_inj_last)
        self.PIDDYaw_inj = ((-self.Imu1AngleYaw) - self.PIDDYaw_inj_last)
        self.PIDDPitch_inj_last = (-self.Imu1AnglePitch)
        self.PIDDRoll_inj_last = (-self.Imu1AngleRoll)
        self.PIDDYaw_inj_last = (-self.Imu1AngleYaw)

    #------------------------------------------
    #NTbus data logs: the order must match that of setToStandardNTLoggerItemList()
    def getDataLine(self):
        dataline = ''
        dataline +=  '{:.1f}'.format(0.001*self.Time) + "\t"

        dataline +=  str(10*self.Imu1received) + "\t"
        dataline +=  str(10*self.Imu1done) + "\t"
        dataline +=  str(10*self.PIDdone) + "\t"
        dataline +=  str(10*self.Motorsdone) + "\t"
        dataline +=  str(10*self.Imu2received) + "\t"
        dataline +=  str(10*self.Imu2done) + "\t"
        dataline +=  str(10*self.Logdone) + "\t"
        dataline +=  str(10*self.Loopdone) + "\t"

        dataline +=  str(self.State) + "\t"
        dataline +=  str(self.Status) + "\t"
        dataline +=  str(self.Status2) + "\t"
        dataline +=  str(self.ErrorCnt) + "\t"
        dataline +=  '{:.3f}'.format(0.001 * self.Voltage) + "\t"

        dataline +=  str(self.ax1) + "\t" + str(self.ay1) + "\t" + str(self.az1) + "\t"
        dataline +=  str(self.gx1) + "\t" + str(self.gy1) + "\t" + str(self.gz1) + "\t"
        dataline +=  str(self.Imu1State) + "\t"
        dataline +=  str(self.ax2) + "\t" + str(self.ay2) + "\t" + str(self.az2) + "\t"
        dataline +=  str(self.gx2) + "\t" + str(self.gy2) + "\t" + str(self.gz2) + "\t"
        dataline +=  str(self.Imu2State) + "\t"

        if self.logVersion==cLOGVERSION_NT_V3:
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu1AnglePitch ) + "\t"
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu1AngleRoll ) + "\t"
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu1AngleYaw ) + "\t"
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu2AnglePitch ) + "\t"
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu2AngleRoll ) + "\t"
            dataline +=  '{:.3f}'.format( 0.001 * self.Imu2AngleYaw ) + "\t"
        else:
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu1AnglePitch ) + "\t"
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu1AngleRoll ) + "\t"
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu1AngleYaw ) + "\t"
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu2AnglePitch ) + "\t"
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu2AngleRoll ) + "\t"
            dataline +=  '{:.2f}'.format( 0.01 * self.Imu2AngleYaw ) + "\t"

        dataline +=  '{:.3f}'.format( self.EncAnglePitch_inj ) + "\t"
        dataline +=  '{:.3f}'.format( self.EncAngleRoll_inj ) + "\t"
        dataline +=  '{:.3f}'.format( self.EncAngleYaw_inj ) + "\t"
        dataline +=  str(self.MotState) + "\t"

        dataline +=  '{:.3f}'.format( 0.001 * self.PIDErrorPitch ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDErrorRoll ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDErrorYaw ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDEffSetPointPitch_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDEffSetPointRoll_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDEffSetPointYaw_inj ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDSetPointPitch ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDSetPointRoll ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDSetPointYaw ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDPanSetPointPitch_inj ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDPanSetPointRoll_inj ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDPanSetPointYaw_inj ) + "\t"

        dataline +=  '{:.3f}'.format( 0.001 * self.PIDPPitch_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDPRoll_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDPYaw_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIPitch ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIRoll ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIYaw ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDPitch ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDRoll ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDYaw ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIPitch_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIRoll_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDIYaw_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDPitch_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDRoll_inj ) + "\t"
        dataline +=  '{:.3f}'.format( 0.001 * self.PIDDYaw_inj ) + "\t"

        dataline +=  '{:.2f}'.format( 0.01 * self.PIDCntrlPitch ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDCntrlRoll ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDCntrlYaw ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDMotorCntrlPitch ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDMotorCntrlRoll ) + "\t"
        dataline +=  '{:.2f}'.format( 0.01 * self.PIDMotorCntrlYaw ) + "\t"

        dataline +=  '{:.4f}'.format(0.0001 * self.Ahrs1Rx) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.Ahrs1Ry) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.Ahrs1Rz) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.fAhrs1AccAmp_inj) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.Ahrs1AccConfidence) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.Ahrs1YawTarget) + "\t"

        dataline +=  str(self.Flags) + "\t"
        dataline +=  str(self.VmaxPitch) + "\t" + str(self.MotPitch) + "\t"
        dataline +=  str(self.VmaxRoll) + "\t"  + str(self.MotRoll) + "\t"
        dataline +=  str(self.VmaxYaw) + "\t"   + str(self.MotYaw) + "\t"
        dataline +=  str(self.dUPitch_inj) + "\t" + str(self.dURoll_inj) + "\t" + str(self.dUYaw_inj) + "\t"

        dataline +=  '{:.4f}'.format(0.0001 * self.q0) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.q1) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.q2) + "\t"
        dataline +=  '{:.4f}'.format(0.0001 * self.q3) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.vx) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.vy) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.vz) + "\t"
        dataline +=  str(self.YawRateCmd) + "\t"
        dataline +=  str(self.SLFCStatus) + "\t" + str(self.SLStatus) + "\t"
        dataline +=  str(self.Storm32LinkFailsafeCnt) + "\t" + str(self.A1ValidFailCnt) + "\t"
        dataline +=  str(self.CmdStorm32LinkData_received) + "\t"

        dataline +=  str(self.ax1raw) + "\t" + str(self.ay1raw) + "\t" + str(self.az1raw) + "\t"
        dataline +=  str(self.gx1raw) + "\t" + str(self.gy1raw) + "\t" + str(self.gz1raw) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.temp1) + "\t"

        dataline +=  str(self.ax2raw) + "\t" + str(self.ay2raw) + "\t" + str(self.az2raw) + "\t"
        dataline +=  str(self.gx2raw) + "\t" + str(self.gy2raw) + "\t" + str(self.gz2raw) + "\t"
        dataline +=  '{:.2f}'.format(0.01 * self.temp2) + "\t"

        dataline +=  str( self.EncRawPitch ) + "\t" + str( self.EncRawRoll ) + "\t" + str( self.EncRawYaw ) + "\t"
        dataline +=  str(self.dURawPitch) + "\t" + str(self.dURawRoll) + "\t" + str(self.dURawYaw) + "\t"

        dataline +=  str(self.CameraModel) + "\t"
        dataline +=  str(self.CameraCmd) + "\t" + str(self.CameraValue) + "\t" + str(self.CameraPwm) + "\t"
        dataline +=  str(self.CameraCmd2) + "\t" + str(self.CameraValue2) + "\t"

        dataline +=  str(5*self.InputPitch) + "\t"
        dataline +=  str(5*self.InputRoll) + "\t"
        dataline +=  str(5*self.InputYaw) + "\t"
        dataline +=  str(5*self.InputPanMode) + "\t"
        dataline +=  str(5*self.InputStandBy) + "\t"
        dataline +=  str(5*self.InputCamera) + "\t"
        dataline +=  str(5*self.InputReCenterCamera) + "\t"
        dataline +=  str(5*self.InputScript1) + "\t"
        dataline +=  str(5*self.InputScript2) + "\t"
        dataline +=  str(5*self.InputScript3) + "\t"
        dataline +=  str(5*self.InputScript4) + "\t"
        dataline +=  str(5*self.InputPwmOut) + "\t"
        dataline +=  str(5*self.InputCamera2) + "\t"

#STL
        '''
#XX        dataline +=  str(self.debug1) + "\t" +  str(self.debug2) + "\t" +  str(self.debug3) + "\t"
#XX        dataline +=  str(self.debug4) + "\t" +  str(self.debug5) + "\t" +  str(self.debug6) + "\t"
#XX        dataline +=  str(self.debug7) + "\t"
#XX        dataline +=  str(self.dbg_inj1) + "\t" +  str(self.dbg_inj2) + "\t" +  str(self.dbg_inj3) + "\n"
#angles, velocities
#        sform = '{:.2f}'; sfact = 0.01
#accelerations
#        sform = '{:.3f}'; sfact = 0.001
        sform = '{:.3f}'; sfact = 0.001
        dataline +=  sform.format(sfact*self.debug1) + "\t" +  sform.format(sfact*self.debug2) + "\t" +  sform.format(sfact*self.debug3) + "\t"
        dataline +=  sform.format(sfact*self.debug4) + "\t" +  sform.format(sfact*self.debug5) + "\t" +  sform.format(sfact*self.debug6) + "\t"
##        dataline +=  str(self.ax1*9.81/8048) + "\t" + str(self.ay1*9.81/8048) + "\t" + str(self.az1*9.81/8048) + "\t"

        dataline +=  str(self.debug7) + "\t" # = numSat
#        accest = sqrt(self.debug1*self.debug1 + self.debug2*self.debug2)
#        dataline +=  sform.format(sfact*accest) + "\t"

        self.dbg_inj1 = self.ax1*9.81/8048 - sfact*self.debug4
        self.dbg_inj2 = self.ay1*9.81/8048 - sfact*self.debug5
        self.dbg_inj3 = self.az1*9.81/8048 - sfact*self.debug6
        dataline +=  str(self.dbg_inj1) + "\t" + str(self.dbg_inj2) + "\t" + str(self.dbg_inj3) + "\n"

#velocity
#        sform = '{:.2f}'; sfact = 0.01
#        dataline +=  sform.format(sfact*self.stl_debug4) + "\t" +  sform.format(sfact*self.stl_debug5) + "\t" +  sform.format(sfact*self.stl_debug6) + "\t"

        alpha = 0.4
        beta = 0.2

        if self.SLStatus >= 125: #new value

            dt = 0.000001*self.Time - self.t_last
            self.t_last = 0.000001*self.Time

            sform = '{:.2f}'; sfact = 0.01
            vx_meas = sfact*self.vx
            vy_meas = sfact*self.vy
            vz_meas = sfact*self.vz

            vx_pred = self.vn_x + self.an_x * dt
            vy_pred = self.vn_y + self.an_y * dt
            vz_pred = self.vn_z + self.an_z * dt

            vx_innov = vx_meas - vx_pred
            vy_innov = vy_meas - vy_pred
            vz_innov = vz_meas - vz_pred

            self.vn_x = vx_pred + alpha * vx_innov  # (1-alpha) v_x + alpha debug4
            self.vn_y = vy_pred + alpha * vy_innov
            self.vn_z = vz_pred + alpha * vz_innov

            if self.t_last > 0.0000000001:
                self.an_x += beta/dt * vx_innov
                self.an_y += beta/dt * vy_innov
                self.an_z += beta/dt * vz_innov

                self.dbg_inj1 = (vx_meas - self.vx_last )/dt
                self.dbg_inj2 = (vy_meas - self.vy_last )/dt
                self.dbg_inj3 = (vz_meas - self.vz_last )/dt

            #just to keep them
            self.vx_last = vx_meas
            self.vy_last = vy_meas
            self.vz_last = vz_meas

#        dataline +=  str(self.an_x) + "\t" +  str(self.vn_x) + "\t" +  str(self.stl_inj1) + "\t" #injected
         '''
        dataline +=  str(self.debug1) + "\t" +  str(self.debug2) + "\t" +  str(self.debug3) + "\t"
        dataline +=  str(self.debug4) + "\t" +  str(self.debug5) + "\t" +  str(self.debug6) + "\t"
        dataline +=  str(self.debug7) + "\t"
        dataline +=  str(self.dbg_inj1) + "\t" +  str(self.dbg_inj2) + "\t" +  str(self.dbg_inj3) + "\n"

        return dataline

    def getGyroFlowDataLine(self):
        dataline = ''
        dataline +=  str(int(self.Time/1500)) + ','
        dataline +=  str(self.gx1raw) + ',' + str(self.gy1raw) + ',' + str(self.gz1raw) + ','
        dataline +=  str(self.ax1raw) + ',' + str(self.ay1raw) + ',' + str(self.az1raw) + "\n"

        return dataline


#this is a child class for handling NT log data
# it implements the unpacking of the received payload bytes
class cNTLogDataFrame(cNTLogDataFrameBase):

    def __init__(self):
        super().__init__()

        #structures of data as stored in NT log files, recorded by a NT Logger
        self.setLoggerStruct_V3 = struct.Struct('=I'+'BBBBBBB'+'HHHHH'+'iiiiii')
        self.cmdEncoderStruct = struct.Struct('=hhhB')
        self.setMotorAllStruct = struct.Struct('=BBhBhBh')
        self.setCameraStruct = struct.Struct('=BBBBH')
        self.cmdAccGyroStruct_V2 = struct.Struct('=hhhhhhB')
        self.cmdAccGyroRawStruct_V2 = struct.Struct('=hhhhhhh')
        self.cmdPidInStruct = struct.Struct('=iiihhh')
        self.cmdPidIDStruct = struct.Struct('=hhhhhh')
        self.cmdPidOutStruct = struct.Struct('=hhhhhh')
        self.cmdAhrsStruct = struct.Struct('=hhhhh')
        self.cmdStorm32LinkDataStruct = struct.Struct('=hhhhhhhhBB')
        self.cmdStorm32LinkDataStruct_V2 = struct.Struct('=hhhhhhhhBBBB')
        self.cmdDebugDataStruct = struct.Struct('=hhhhhhh')
        self.cmdParameterStruct = struct.Struct('=HHH16s')
        self.cmdTunnelTxStruct = struct.Struct('=B12s')
        self.cmdWriteLoggerDateTimeStruct = struct.Struct('=HBBBBB')
        self.cmdAutopilotSystemTimeStruct = struct.Struct('=Q')
        self.cmdFunctionInputValuesStruct = struct.Struct('=bbbbbbbbbbbbbb')

    def unpackSetLogger(self,payload):
        if self.logVersion == cLOGVERSION_NT_V3:
            self.setLogger_V3( self.setLoggerStruct_V3.unpack(payload) )
        else:
            self.setLogger_V0( self.setLoggerStruct_V0.unpack(payload) )
        self.SetLoggerData_received += 1

    def unpackCmdEncoder(self,payload): #struct.Struct('=hhhB')
        (self.EncRawPitch,self.EncRawRoll,self.EncRawYaw,self.MotState
         ) = self.cmdEncoderStruct.unpack(payload)
        self.CmdEncoderData_received += 1

    def unpackSetMotorAll(self,payload): #struct.Struct('=BBhBhBh')
        (self.Flags,self.VmaxPitch,self.MotPitch,self.VmaxRoll,self.MotRoll,self.VmaxYaw,self.MotYaw
         ) = self.setMotorAllStruct.unpack(payload)
        #if( ntbus_buf[0] & NTBUS_MOTOR_FLAG_FOC ){
        if self.Flags & 0x20 > 0:
            #dU = (u16)(ntbus_buf[1] & 0x7F) + ((u16)(ntbus_buf[2] & 0x7F ) << 7) + ((u16)(ntbus_buf[3] & 0x7F ) << 14); //low byte, high byte, highest byte
            #if( dU & (1<<20) ) dU |= 0xFFF00000; //if 20th bit is set, restore that it's a negative value
            #do this first, so that we have the original values
            # the brackets are most important!
            self.dURawPitch = (self.VmaxPitch & 0x007f) + ((self.MotPitch & 0x007f) << 7) + ((self.MotPitch & 0x7f00) << 6)
            if self.dURawPitch > (1<<20): self.dURawPitch = self.dURawPitch - (1<<21)
            self.dURawRoll = (self.VmaxRoll & 0x007f) + ((self.MotRoll & 0x007f) << 7) + ((self.MotRoll & 0x7f00) << 6)
            if self.dURawRoll > (1<<20): self.dURawRoll = self.dURawRoll - (1<<21)
            self.dURawYaw = (self.VmaxYaw & 0x007f) + ((self.MotYaw & 0x007f) << 7) + ((self.MotYaw & 0x7f00) << 6)
            if self.dURawYaw > (1<<20): self.dURawYaw = self.dURawYaw - (1<<21)
            self.VmaxPitch = self.MotPitch = self.VmaxRoll = self.MotRoll = self.VmaxYaw = self.MotYaw = 0
        else:
            #Vmax,Mot were decoded alread by NTLogger
            self.dURawPitch = self.dURawRoll = self.dURawYaw = 0
        self.SetMotorAllData_received += 1

    def unpackSetCamera(self,payload): #struct.Struct('=BBBBH')
        (self.CameraFlags,b2,b3,b4,b5) = self.setCameraStruct.unpack(payload)
        if self.CameraFlags & 0x40 > 0:
            (self.CameraCmd2,self.CameraValue2) = (b2,b3)
        else:
            (self.CameraModel,self.CameraCmd,self.CameraValue,self.CameraPwm) = (b2,b3,b4,b5)
        self.SetCameraData_received += 1

    def unpackCmdAccGyro1_V2(self,payload): #struct.Struct('=hhhhhhB')
        (self.ax1,self.ay1,self.az1,self.gx1,self.gy1,self.gz1,self.Imu1State
         ) = self.cmdAccGyroStruct_V2.unpack(payload)
        self.CmdAccGyro1Data_received += 1

    def unpackCmdAccGyro2_V2(self,payload): #struct.Struct('=hhhhhhB')
        (self.ax2,self.ay2,self.az2,self.gx2,self.gy2,self.gz2,self.Imu2State
         ) = self.cmdAccGyroStruct_V2.unpack(payload)
        self.CmdAccGyro2Data_received += 1

    def unpackCmdAccGyro1Raw_V2(self,payload): #struct.Struct('=hhhhhhh')
        (self.ax1raw,self.ay1raw,self.az1raw,self.gx1raw,self.gy1raw,self.gz1raw,self.temp1
         ) = self.cmdAccGyroRawStruct_V2.unpack(payload)
        self.CmdAccGyro1RawData_received += 1

    def unpackCmdAccGyro2Raw_V2(self,payload): #struct.Struct('=hhhhhhh')
        (self.ax2raw,self.ay2raw,self.az2raw,self.gx2raw,self.gy2raw,self.gz2raw,self.temp2
         ) =  self.cmdAccGyroRawStruct_V2.unpack(payload)
        self.CmdAccGyro2RawData_received += 1

    def unpackCmdPidIn(self,payload): #struct.Struct('=iiihhh')
        (self.PIDErrorPitch,self.PIDErrorRoll,self.PIDErrorYaw,
         self.PIDSetPointPitch,self.PIDSetPointRoll,self.PIDSetPointYaw
         ) = self.cmdPidInStruct.unpack(payload)
        self.CmdPidInData_received += 1

    def unpackCmdPidID(self,payload): #struct.Struct('=hhhhhh')
        (self.PIDIPitch,self.PIDIRoll,self.PIDIYaw,
         self.PIDDPitch,self.PIDDRoll,self.PIDDYaw
         ) = self.cmdPidIDStruct.unpack(payload)
        self.CmdPidIDData_received += 1

    def unpackCmdPidOut(self,payload): #struct.Struct('=hhhhhh')
        (self.PIDCntrlPitch,self.PIDCntrlRoll,self.PIDCntrlYaw,
         self.PIDMotorCntrlPitch,self.PIDMotorCntrlRoll,self.PIDMotorCntrlYaw
         ) = self.cmdPidOutStruct.unpack(payload)
        self.CmdPidOutData_received += 1

    def unpackCmdAhrs1(self,payload): #struct.Struct('=hhhhh')
        (self.Ahrs1Rx,self.Ahrs1Ry,self.Ahrs1Rz,self.Ahrs1AccConfidence,self.Ahrs1YawTarget
         ) = self.cmdAhrsStruct.unpack(payload)
        self.CmdAhrs1Data_received += 1
        
    def unpackCmdAhrs2(self,payload): #struct.Struct('=hhhhh')
        (self.Ahrs2Rx,self.Ahrs2Ry,self.Ahrs2Rz,self.Ahrs2AccConfidence,self.Ahrs2YawTarget
         ) = self.cmdAhrsStruct.unpack(payload)
        self.CmdAhrs2Data_received += 1

    def unpackCmdStorm32LinkData(self,payload): #struct.Struct('=hhhhhhhhBB')
        (self.q0,self.q1,self.q2,self.q3,self.vx,self.vy,self.vz,
         self.YawRateCmd,self.SLFCStatus,self.SLStatus
         ) = self.cmdStorm32LinkDataStruct.unpack(payload)
        self.CmdStorm32LinkData_received += 1

    def unpackCmdStorm32LinkData_V2(self,payload): #struct.Struct('=hhhhhhhhBBBB')
        (self.q0,self.q1,self.q2,self.q3,self.vx,self.vy,self.vz,
        self.YawRateCmd,self.SLFCStatus,self.SLStatus,self.Storm32LinkFailsafeCnt,self.A1ValidFailCnt
         ) = self.cmdStorm32LinkDataStruct_V2.unpack(payload)
        self.CmdStorm32LinkData_received += 1

    def unpackCmdDebugData(self,payload): #struct.Struct('=hhhhhhh')
        (self.debug1,self.debug2,self.debug3,self.debug4,self.debug5,self.debug6,self.debug7,
         ) = self.cmdDebugDataStruct.unpack(payload)
        self.CmdDebugData_received += 1

    def unpackCmdParameter(self,payload):
        (self.ParameterAdr,self.ParameterValue,self.ParameterFormat,self.ParameterNameStr
         ) = self.cmdParameterStruct.unpack(payload)
        if self.ParameterFormat == 2: #PARAM_TYPE_INT8 = 2
            #if self.ParameterValue>128: self.ParameterValue -= 256
            if self.ParameterValue > 32768: self.ParameterValue -= 65536 #int8 is promoted to int16 by how it's stored
        if self.ParameterFormat == 4: #PARAM_TYPE_INT16 = 4
            if self.ParameterValue > 32768: self.ParameterValue -= 65536

    def unpackCmdTunnelTx(self,payload):
        (self.TunnelTxLen,self.TunnelTxData) = self.cmdTunnelTxStruct.unpack(payload)
        self.CmdTunnelTx_received += 1

    def unpackCmdWriteLoggerDateTime(self,payload):
        (self.RtcYear,self.RtcMonth,self.RtcDay,self.RtcHour,self.RtcMinute,self.RtcSecond
         ) = self.cmdWriteLoggerDateTimeStruct.unpack(payload)
        self.CmdWriteLoggerDateTime_received += 1

    def unpackCmdAutopilotSystemTime(self,payload):
        (self.UnixTime) = self.cmdAutopilotSystemTimeStruct.unpack(payload)
        self.CmdAutopilotSystemTime_received += 1

    def unpackCmdFunctionInputValues(self,payload):
        (self.InputPitch,self.InputRoll,self.InputYaw,self.InputPanMode,self.InputStandBy,
         self.InputCamera,self.InputReCenterCamera,self.InputScript1,self.InputScript2,self.InputScript3,self.InputScript4,
         self.InputPwmOut,self.InputCamera2,b14) = self.cmdFunctionInputValuesStruct.unpack(payload)
        self.CmdFunctionInputValues_received += 1

    def doSetLogger(self,payload): self.unpackSetLogger(payload); return True
    def doSetMotorAll(self,payload): self.unpackSetMotorAll(payload); return True
    def doSetCamera(self,payload): self.unpackSetCamera(payload); return True
    def doCmdAccGyro1_V2(self,payload): self.unpackCmdAccGyro1_V2(payload); return True
    def doCmdAccGyro2_V2(self,payload): self.unpackCmdAccGyro2_V2(payload); return True
    def doCmdAccGyro1Raw_V2(self,payload): self.unpackCmdAccGyro1Raw_V2(payload); return True
    def doCmdAccGyro2Raw_V2(self,payload): self.unpackCmdAccGyro2Raw_V2(payload); return True
    def doCmdPidIn(self,payload): self.unpackCmdPidIn(payload); return True
    def doCmdPidID(self,payload): self.unpackCmdPidID(payload); return True
    def doCmdPidOut(self,payload): self.unpackCmdPidOut(payload); return True
    def doCmdAhrs1(self,payload): self.unpackCmdAhrs1(payload); return True
    def doCmdAhrs2(self,payload): self.unpackCmdAhrs2(payload); return True
    def doCmdEncoder(self,payload): self.unpackCmdEncoder(payload); return True
    def doCmdStorm32LinkData(self,payload): self.unpackCmdStorm32LinkData(payload); return True
    def doCmdStorm32LinkData_V2(self,payload): self.unpackCmdStorm32LinkData_V2(payload); return True
    def doCmdDebugData(self,payload): self.unpackCmdDebugData(payload); return True
    def doCmdParameter(self,payload): self.unpackCmdParameter(payload); return True
    def doCmdTunnelTx(self,payload): self.unpackCmdTunnelTx(payload); return True
    def doCmdWriteLoggerDateTime(self,payload): self.unpackCmdWriteLoggerDateTime(payload); return True
    def doCmdAutopilotSystemTime(self,payload): self.unpackCmdAutopilotSystemTime(payload); return True
    def doCmdFunctionInputValues(self,payload): self.unpackCmdFunctionInputValues(payload); return True

#these constants are required by the serial data frame, to be able to unpack the bytes correctly
cSETLOGGER_V3_DATALEN             = 36
cSETLOGGER_V3_HIGHBITSLEN         = 6
cSETLOGGER_V3_FRAMELEN            = 36 + 6 #+ 1
cSETMOTORALL_DATALEN              = 10
cSETMOTORALL_FRAMELEN             = 10 #10 + 1
cSETCAMERA_DATALEN                = 5
cSETCAMERA_FRAMELEN               = 5 #5 + 1
cCMDENCODERDATA_DATALEN           = 7
cCMDENCODERDATA_HIGHBITSLEN       = 2
cCMDENCODERDATA_FRAMELEN          = 7 + 2 #7 + 2 + 1
cCMDACCGYRODATA_V2_DATALEN        = 13
cCMDACCGYRODATA_V2_HIGHBITSLEN    = 2
cCMDACCGYRODATA_V2_FRAMELEN       = 13 + 2 #13 + 2 + 1
cCMDACCGYRORAWDATA_V2_DATALEN     = 14
cCMDACCGYRORAWDATA_V2_HIGHBITSLEN = 2
cCMDACCGYRORAWDATA_V2_FRAMELEN    = 14 + 2 #14 + 2 + 1
cCMDPIDINDATA_DATALEN             = 15
cCMDPIDINDATA_HIGHBITSLEN         = 4
cCMDPIDINDATA_FRAMELEN            = 15 + 4 #15 + 4 + 1
cCMDPIDIDDATA_DATALEN             = 12
cCMDPIDIDDATA_HIGHBITSLEN         = 2
cCMDPIDIDDATA_FRAMELEN            = 12 + 2 #12 + 2 + 1
cCMDPIDOUTDATA_DATALEN            = 12
cCMDPIDOUTDATA_HIGHBITSLEN        = 2
cCMDPIDOUTDATA_FRAMELEN           = 12 + 2 #12 + 2 + 1
cCMDAHRSDATA_DATALEN              = 10
cCMDAHRSDATA_HIGHBITSLEN          = 2
cCMDAHRSDATA_FRAMELEN             = 10 + 2 #10 + 2 + 1
cCMDSTORM32LINKDATA_DATALEN       = 18
cCMDSTORM32LINKDATA_HIGHBITSLEN   = 4
cCMDSTORM32LINKDATA_FRAMELEN      = 18 + 4 #18 + 2 + 1
cCMDSTORM32LINKDATA_V2_DATALEN    = 20
cCMDSTORM32LINKDATA_V2_HIGHBITSLEN   = 4
cCMDSTORM32LINKDATA_V2_FRAMELEN   = 20 + 4 #20 + 2 + 1
cCMDDEBUGDATA_DATALEN             = 14
cCMDDEBUGDATA_HIGHBITSLEN         = 2
cCMDDEBUGDATA_FRAMELEN            = 14 + 2 #18 + 2 + 1
cCMDTUNNELTX_DATALEN              = 12
cCMDTUNNELTX_HIGHBITSLEN          = 2
cCMDTUNNELTX_FRAMELEN             = 12 + 2 #12 + 2 + 1
cCMDWRITELOGGERDATETIME_DATALEN         = 7
cCMDWRITELOGGERDATETIME_HIGHBITSLEN     = 2
cCMDWRITELOGGERDATETIME_FRAMELEN        = 7 + 2 #7 + 2 + 1
cCMDAUTOPILOTSYSTEMTIME_DATALEN         = 8
cCMDAUTOPILOTSYSTEMTIME_HIGHBITSLEN     = 2
cCMDAUTOPILOTSYSTEMTIME_FRAMELEN        = 8 + 2 #8 + 2 + 1
cCMDFUNCTIONINPUTVALUES_DATALEN         = 14
cCMDFUNCTIONINPUTVALUES_HIGHBITSLEN     = 2
cCMDFUNCTIONINPUTVALUES_FRAMELEN        = 14 + 2 #14 + 2 + 1

#this is a child class for handling NT serial data streams
# it does the encoding of the data onto the NT bus
# Note: the data on the NTBus can be in a different format than the data in the NT log file
#the reader must provide a function
# reader.readPayload(length)
#the payloads here are always None, since each function reads its bytes itself by calling reader.readPayload() 
#
# a frame error must ONLY be thrown, then one of the crucial packages is wrong,
# i.e. SetLogger, SetMotorAll !!
class cNTLogSerialDataFrame(cNTLogDataFrame):

    def __init__(self, _reader):
        super().__init__()
        self.reader = _reader

        #structures of data as transmitted on the NT bus, recorded by a USB-TTL adapter
        # differs for SetMotAll, SetLog, and SetCamera from the data in a NT log file
        # these thus need special handling
        self.setLoggerStruct_V3_NTbus = struct.Struct('=I'+'BBBBBBB'+'HHHHH'+'hhhhhh'+'BBB')
        self.setCameraStruct_NTBus = struct.Struct('=BBBBB')
        self.cmdPidInStruct_NTbus = struct.Struct('=hhhBBBhhh')

        self.setLogVersion(cLOGVERSION_NT_LATEST) #tells its latest version, not needed as done by __init__(), but be explicit

    def doSetLogger(self,payload):
        (b,err) = self.reader.readPayload(cSETLOGGER_V3_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_SETLOGERROR #; return !!IT MUST NOT BE REJECTED FOR SETLOG!!
        payload = self.decode(b, cSETLOGGER_V3_DATALEN, cSETLOGGER_V3_HIGHBITSLEN)
        #if payload!=None and not self.checkReaderError(): !!IT MUST NOT BE REJECTED FOR SETLOG!!!
        #self.unpackSetLogger(payload)
        #self.setLogger( self.setLoggerStruct_V3_NTbus.unpack(payload) )
        (self.TimeStamp32,
         self.Imu1received,self.Imu1done,self.PIDdone,self.Motorsdone,
         self.Imu2done,self.Logdone,self.Loopdone,
         self.State,self.Status,self.Status2,self.ErrorCnt,self.Voltage,
         self.Imu1AnglePitch,self.Imu1AngleRoll,self.Imu1AngleYaw,
         self.Imu2AnglePitch,self.Imu2AngleRoll,self.Imu2AngleYaw,
         self.highres1,self.highres2,self.highres3,
        ) = self.setLoggerStruct_V3_NTbus.unpack(payload)
        self.Imu1AnglePitch = self.Imu1AnglePitch*16 + (self.highres1 & 0x0f)
        self.Imu1AngleRoll = self.Imu1AngleRoll*16 + (self.highres2 & 0x0f)
        self.Imu1AngleYaw = self.Imu1AngleYaw*16 + (self.highres3 & 0x0f)
        self.Imu2AnglePitch = self.Imu2AnglePitch*16 + ((self.highres1 >> 4) & 0x0f)
        self.Imu2AngleRoll = self.Imu2AngleRoll*16 + ((self.highres2 >> 4) & 0x0f)
        self.Imu2AngleYaw = self.Imu2AngleYaw*16 + ((self.highres3 >> 4) & 0x0f)
        self.SetLoggerData_received += 1
        return True

    def doCmdEncoder(self,payload):
        (b,err) = self.reader.readPayload(cCMDENCODERDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDENCODERDATA_DATALEN, cCMDENCODERDATA_HIGHBITSLEN)
        self.unpackCmdEncoder(payload)
        #BUG: done already in unpackXX() self.CmdEncoderData_received += 1
        return True

    def doSetMotorAll(self,payload):
        (b,err) = self.reader.readPayload(cSETMOTORALL_FRAMELEN)
        if err or self.crcError(b,): self.error |= cNTDATAFRAME_SETMOTERROR; return False
        payload = b
        self.unpackSetMotorAll(payload)
        if self.Flags & 0x20 > 0:
            #has been decoded already by self.unpackSetMotorAll() !
            self.VmaxPitch = self.MotPitch = self.VmaxRoll = self.MotRoll = self.VmaxYaw = self.MotYaw = 0
        else:
            # p->VmaxPitch <<= 1;//ntbus_buf[1]
            # a = (u16)(ntbus_buf[2]) + ((u16)(ntbus_buf[3]) << 7);
            self.VmaxPitch <<= 1
            self.MotPitch = (self.MotPitch & 0x00ff) + ((self.MotPitch & 0xff00) >> 1)
            self.VmaxRoll <<= 1
            self.MotRoll = (self.MotRoll & 0x00ff) + ((self.MotRoll & 0xff00) >> 1)
            self.VmaxYaw <<= 1
            self.MotYaw = (self.MotYaw & 0x00ff) + ((self.MotYaw & 0xff00) >> 1)
            self.dURawPitch = self.dURawRoll = self.dURawYaw = 0
        #ARG bug, has been incremented already in unpackSetMotorAll() self.SetMotorAllData_received += 1
        return True

    def doSetCamera(self,payload):
        (b,err) = self.reader.readPayload(cSETCAMERA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        (self.CameraFlags,b2,b3,b4,b5) = self.setCameraStruct_NTBus.unpack(b)
        if self.CameraFlags & 0x40 > 0:
            (self.CameraCmd2, self.CameraValue2) = (b2,b3)
            if self.CameraValue2 > 0: self.CameraValue2 = (self.CameraValue2-1) * 10 + 1000
        else:
            (self.CameraModel, self.CameraCmd, self.CameraValue, self.CameraPwm) = (b2,b3,b4,b5)
            if self.CameraValue > 0: self.CameraValue = (self.CameraValue-1) * 10 + 1000
            if self.CameraPwm > 0: self.CameraPwm = (self.CameraPwm-1) * 10 + 1000
        self.SetCameraData_received += 1
        return True

    def doCmdAccGyro1_V2(self,payload):
        (b,err) = self.reader.readPayload(cCMDACCGYRODATA_V2_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDACCGYRODATA_V2_DATALEN, cCMDACCGYRODATA_V2_HIGHBITSLEN)
        self.unpackCmdAccGyro1_V2(payload)
        #BUG: done already in unpackXX() self.CmdAccGyro1Data_received += 1
        return True

    def doCmdAccGyro2_V2(self,payload):
        (b,err) = self.reader.readPayload(cCMDACCGYRODATA_V2_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDACCGYRODATA_V2_DATALEN, cCMDACCGYRODATA_V2_HIGHBITSLEN)
        self.unpackCmdAccGyro2_V2(payload)
        #BUG: done already in unpackXX() self.CmdAccGyro2Data_received += 1
        return True

    def doCmdAccGyro1Raw_V2(self,payload):
        (b,err) = self.reader.readPayload(cCMDACCGYRORAWDATA_V2_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDACCGYRORAWDATA_V2_DATALEN, cCMDACCGYRORAWDATA_V2_HIGHBITSLEN)
        self.unpackCmdAccGyro1Raw_V2(payload)
        #BUG: done already in unpackXX() self.CmdAccGyro1RawData_received += 1
        return True

    def doCmdAccGyro2Raw_V2(self,payload):
        (b,err) = self.reader.readPayload(cCMDACCGYRORAWDATA_V2_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDACCGYRORAWDATA_V2_DATALEN, cCMDACCGYRORAWDATA_V2_HIGHBITSLEN)
        self.unpackCmdAccGyro2Raw_V2(payload)
        #BUG: done already in unpackXX() self.CmdAccGyro2RawData_received += 1
        return True

    def doCmdPidIn(self,payload):
        (b,err) = self.reader.readPayload(cCMDPIDINDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDPIDINDATA_DATALEN, cCMDPIDINDATA_HIGHBITSLEN)
        (self.PIDErrorPitch,self.PIDErrorRoll,self.PIDErrorYaw,
         self.highres1,self.highres2,self.highres3,
         self.PIDSetPointPitch,self.PIDSetPointRoll,self.PIDSetPointYaw
        ) = self.cmdPidInStruct_NTbus.unpack(payload)
        self.PIDErrorPitch = self.PIDErrorPitch*16 + (self.highres1 & 0x0f)
        self.PIDErrorRoll = self.PIDErrorRoll*16 + (self.highres2 & 0x0f)
        self.PIDErrorYaw = self.PIDErrorYaw*16 + (self.highres3 & 0x0f)
        self.CmdPidInData_received += 1
        return True

    def doCmdPidID(self,payload):
        (b,err) = self.reader.readPayload(cCMDPIDIDDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDPIDIDDATA_DATALEN, cCMDPIDIDDATA_HIGHBITSLEN)
        self.unpackCmdPidID(payload)
        #BUG: done already in unpackXX() self.CmdPidIDData_received += 1
        return True

    def doCmdPidOut(self,payload):
        (b,err) = self.reader.readPayload(cCMDPIDOUTDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDPIDOUTDATA_DATALEN, cCMDPIDOUTDATA_HIGHBITSLEN)
        self.unpackCmdPidOut(payload)
        #BUG: done already in unpackXX() self.CmdPidOutData_received += 1
        return True

    def doCmdAhrs1(self,payload):
        (b,err) = self.reader.readPayload(cCMDAHRSDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDAHRSDATA_DATALEN, cCMDAHRSDATA_HIGHBITSLEN)
        self.unpackCmdAhrs1(payload)
        #BUG: done already in unpackXX() self.CmdAhrs1Data_received += 1
        return True

    def doCmdStorm32LinkData(self,payload):
        (b,err) = self.reader.readPayload(cCMDSTORM32LINKDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDSTORM32LINKDATA_DATALEN, cCMDSTORM32LINKDATA_HIGHBITSLEN)
        self.unpackCmdStorm32LinkData(payload)
        #BUG: done already in unpackXX() self.CmdStorm32LinkData_received += 1
        return True

    def doCmdStorm32LinkData_V2(self,payload):
        (b,err) = self.reader.readPayload(cCMDSTORM32LINKDATA_V2_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDSTORM32LINKDATA_V2_DATALEN, cCMDSTORM32LINKDATA_V2_HIGHBITSLEN)
        self.unpackCmdStorm32LinkData_V2(payload)
        #BUG: done already in unpackXX() self.CmdStorm32LinkData_received += 1
        return True

    def doCmdDebugData(self,payload):
        (b,err) = self.reader.readPayload(cCMDDEBUGDATA_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDDEBUGDATA_DATALEN, cCMDDEBUGDATA_HIGHBITSLEN)
        self.unpackCmdDebugData(payload)
        #BUG: done already in unpackXX() self.CmdDebugData_received += 1
        return True

    def doCmdParameter(self,payload):
        return False

    def doCmdTunnelTx(self,payload):
        (b,err) = self.reader.readPayload(cCMDTUNNELTX_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDTUNNELTX_DATALEN, cCMDTUNNELTX_HIGHBITSLEN)
        self.unpackCmdTunnelTx(payload)
        #BUG: done already in unpackXX() self.CmdTunnelTx_received += 1
        return True

    def doCmdWriteLoggerDateTime(self,payload):
        return False

    def doCmdAutopilotSystemTime(self,payload):
        (b,err) = self.reader.readPayload(cCMDAUTOPILOTSYSTEMTIME_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDAUTOPILOTSYSTEMTIME_DATALEN, cCMDAUTOPILOTSYSTEMTIME_HIGHBITSLEN)
        self.unpackCmdAutopilotSystemTime(payload)
        #BUG: done already in unpackXX() self.CmdAutopilotSystemTime_received += 1
        return True

    def doCmdFunctionInputValues(self,payload):
        (b,err) = self.reader.readPayload(cCMDFUNCTIONINPUTVALUES_FRAMELEN)
        if err or self.crcError(b): self.error |= cNTDATAFRAME_CMDERROR; return False
        payload = self.decode(b, cCMDFUNCTIONINPUTVALUES_DATALEN, cCMDFUNCTIONINPUTVALUES_HIGHBITSLEN)
        self.unpackCmdFunctionInputValues(payload)
        #BUG: done already in unpackXX() self.CmdFunctionInputValues_received += 1
        return True

    def readCmdByte(self):
        (b,err) = self.reader.readPayload(1)
        if err: return 255 #hopefully a really invalid CmdByte
        return int(b[0])

    def decode(self,b,datalen,highbitslen): #returns a bytearray of the raw values
        highbits = b[datalen:datalen+highbitslen]
        highbytenr = 0
        bitpos = 0x01
        d = bytearray()
        crc = 0
        for n in range(datalen):
            if bitpos == 0x80:
                highbytenr += 1
                bitpos = 0x01
            c = b[n]
            if highbits[highbytenr] & bitpos: c |= 0x80
            d.append(c)
            crc = crc ^ c
            bitpos <<= 1
        return d

    def crcError(self,payload):
        (b,err) = self.reader.readPayload(1)
        if err: return True
        crc = int(b[0])
        crcpayload = 0
        for n in range(len(payload)): crcpayload = crcpayload ^ payload[n]
        if crcpayload != crc: return True
        return False


###############################################################################
# cNTLogParser
# this is the main class to parse a stream of log packets into a cNTLogDataFrame
#-----------------------------------------------------------------------------#
cCMD_RES    = 0x50 #'RES ';
cCMD_SET    = 0x40 #'SET ';
cCMD_GET    = 0x30 #'GET ';
cCMD_TRG    = 0x10 #'TRG ';
cCMD_CMD    = 0x00 #'CMD ';

cID_ALL     = 0  #'ALL  ';
cID_IMU1    = 1  #'IMU1 '
cID_IMU2    = 2  #'IMU2 '
cID_MOTA    = 3  #'MOTA ';
cID_MOTP    = 4  #'MOTP ';
cID_MOTR    = 5  #'MOTR ';
cID_MOTY    = 6  #'MOTY ';
cID_CAMERA  = 7  #'CAM  ';
cID_LOG     = 11 #'LOG  '; 0x0B
cID_IMU3    = 12 #'IMU3 '

cRESALL     = 0x80 + cCMD_RES + cID_ALL  #0xD0
cTRGALL     = 0x80 + cCMD_TRG + cID_ALL  #0x90
cGETIMU1    = 0x80 + cCMD_GET + cID_IMU1 #0xB1
cGETIMU2    = 0x80 + cCMD_GET + cID_IMU2 #0xB2
cGETIMU3    = 0x80 + cCMD_GET + cID_IMU3 #0xBC
cGETMOTP    = 0x80 + cCMD_GET + cID_MOTP #0xB4
cGETMOTR    = 0x80 + cCMD_GET + cID_MOTR #0xB5
cGETMOTY    = 0x80 + cCMD_GET + cID_MOTY #0xB6
cSETMOTA    = 0x80 + cCMD_SET + cID_MOTA #0xC3
cSETCAMERA  = 0x80 + cCMD_SET + cID_CAMERA
cSETLOG     = 0x80 + cCMD_SET + cID_LOG  #0xCB
cCMDLOG     = 0x80 + cCMD_CMD + cID_LOG  #0x8B

cCMDBYTE_GetStatus              = 1
cCMDBYTE_GetVersion             = 2
cCMDBYTE_GetBoardStr            = 3
cCMDBYTE_GetConfiguration       = 4
cCMDBYTE__ACCGYRO1RAWDATA_V1    = 32 #DEPRECTAED
cCMDBYTE__ACCGYRO2RAWDATA_V1    = 33 #DEPRECTAED
cCMDBYTE__ACCGYRODATA_V1        = 34 #DEPRECTAED
cCMDBYTE_PidOutData             = 35 #CMD LOG  PidData 35
cCMDBYTE_ParameterData          = 36 #CMD LOG  ParameterData 36
cCMDBYTE_Ahrs1Data              = 37 #CMD LOG  Ahrs1Data 37
cCMDBYTE__AHRS2DATA             = 38 #DEPRECATED
cCMDBYTE__ACCGYRO3RAWDATA_V1    = 39 #DEPRECATED
cCMDBYTE_AccGyro1RawData_V2     = 40 #CMD LOG  AccGyro1RawData_V2 40
cCMDBYTE_AccGyro2RawData_V2     = 41 #CMD LOG  AccGyro2RawData_V2 41
cCMDBYTE__ACCGYRO3RAWDATA_V2    = 42 #DEPRECATED
cCMDBYTE_AccGyro1Data_V2        = 43 #CMD LOG  AccGyro1Data_V2 43
cCMDBYTE_AccGyro2Data_V2        = 44 #CMD LOG  AccGyro2Data_V2 44
cCMDBYTE_EncoderData            = 45 #CMD LOG  EncoderData 45
cCMDBYTE_Storm32LinkData        = 46 #CMD LOG  Storm32LinkData 46 0x2E
cCMDBYTE_TunnelTx               = 47 #CMD LOG
cCMDBYTE_TunnelRxGet            = 48
cCMDBYTE_AutopilotSystemTime    = 49 #CMD LOG
cCMDBYTE_PidInData              = 50 #CMD LOG  PidInData 50
cCMDBYTE_FunctionInputValues    = 51 #CMD LOG
cCMDBYTE_PidIDData              = 52 #CMD LOG  PidIDData 52
cCMDBYTE_Storm32LinkData_V2     = 53 #CMD LOG  Storm32LinkData 43
cCMDBYTE_READLOGGERDATETIME     = 114
cCMDBYTE_WRITELOGGERDATETIME    = 115
cCMDBYTE_STOREMOTORCALIBRATION  = 116
cCMDBYTE_READMOTORCALIBRATION   = 117
cCMDBYTE_STOREIMUCALIBRATION    = 118
cCMDBYTE_READIMUCALIBRATION     = 119
cCMDBYTE_DebugData              = 127 #CMD LOG  DebugData 127

cmdbyte_str_dict = {
    32: 'AccGyro1RawData_V1',
    33: 'AccGyro2RawData_V1',
    34: 'AccGyroData_V2',
    38: 'Ahrs2Data',
    39: 'AccGyro3RawData_V1',
    42: 'AccGyro3RawData_V1',
    cCMDBYTE_PidOutData: 'PidOutData',
    cCMDBYTE_ParameterData: 'ParameterData',
    cCMDBYTE_Ahrs1Data: 'Ahrs1Data',
    cCMDBYTE_AccGyro1RawData_V2: 'AccGyro1RawData',
    cCMDBYTE_AccGyro2RawData_V2: 'AccGyro2RawData',
    cCMDBYTE_AccGyro1Data_V2: 'AccGyro1Data',
    cCMDBYTE_AccGyro2Data_V2: 'AccGyro2Data',
    cCMDBYTE_EncoderData: 'EncoderData',
    cCMDBYTE_Storm32LinkData: 'STorM32LinkData_V1',
    cCMDBYTE_Storm32LinkData_V2: 'STorM32LinkData_V2',
    cCMDBYTE_TunnelTx: 'TunnelTx',
    cCMDBYTE_AutopilotSystemTime: 'AutopilotSystemTime',
    cCMDBYTE_PidInData: 'PidInData',
    cCMDBYTE_FunctionInputValues: 'FunctionInputValues',
    cCMDBYTE_PidIDData: 'PidIDData',
    cCMDBYTE_DebugData: 'DebugData',
}

def getCmdByteStr(cmdbyte):
    if cmdbyte in cmdbyte_str_dict:
        return cmdbyte_str_dict[cmdbyte]
    return ''


#the reader must provide a function
# reader.appendDataFrame(frame)
#
# baseTime allows to shift the start time
class cNTLogParser:

    def __init__(self,_frame,_reader,_baseTime=0):
        self.reader = _reader

        self.frame = _frame
        self.frame.clear()

        #the TimeStamp32 CANNOT be 0, so 0 can also be used instead of -1
        self.startTimeStamp32 = 0 #also allows to detect that a first valid data frame was read
        self.lastTimeStamp32 = 0  #is set by a Log packet
        self.TimeStamp32 = 0 #copy of frame.TimeStamp32 for convenience
        self.setLog_received = False #allows to detect that one valid Log was read

        self.logTime_error = False
        self.getImu1_counter, self.getImu2_counter = 0,0
        self.cmdLog36_counter = 0

        self.resAll_counter = 0 #this is used to detect a new log, and is cleared by a SetLog

        self.errorCounts = 0
        self.frameCounts = 0

        self.baseTimeStamp32 = _baseTime #allows to shift the time axis

        #this collects various info which we may want to display extra
        self.cmdParameterData = []
        self.ConfigurationInfoList = []
        self.ParameterDict = {}
        self.Storm32FirmwareVersion = None
        self.ImuOrientation = None
        self.Imu2Orientation = None
        self.NtLogging = None
        self.cmdTunnelTx = []
        self.cmdAutopilotSystemTime = []
        self.AutopilotSystemTime = ''
        self.cmdsLogger = []
        self.cmdsCalibration = []
        self.cmds = []

        self.cmdParameterData_last = '' # is needed to extract firmware version

    def clearForNextDataFrame(self):
        self.frame.clear()
        self.logTime_error = False
        self.getImu1_counter, self.getImu2_counter = 0,0
        self.cmdLog36_counter = 0


    #------------------------------------------
    #get data from reader, and parse into a cNTLogDataFrameObhject()
    def parse(self,cmdid,cmdbyte=None,payload=None): #cmdid = 0x80 + cmd + idbyte
        if cmdid < 128:
            return False #this can't be a cmdid, so skip out fast, and tell caller that the parser did so
        if cmdid==cRESALL: #0x50 # 'RES ';
            self.clearForNextDataFrame();
            self.setLog_received = False
            self.resAll_counter += 1 #this is reset by a SetLog

        elif cmdid==cTRGALL: #'TRG ';'ALL  ';
            pass

        elif cmdid==cSETMOTA: #3 #'SET ';'MOTA ';
            self.frame.doSetMotorAll(payload)

        elif cmdid==cSETCAMERA: #3 #'SET ';'CAM  ';
            self.frame.doSetCamera(payload)

        elif cmdid==cSETLOG: #11 #'SET ';'LOG  ';
            self.lastTimeStamp32 = self.TimeStamp32

            self.frame.doSetLogger(payload)

            self.TimeStamp32 = self.frame.TimeStamp32 #keep a copy for convenience

            if self.startTimeStamp32 <= 0:
                self.startTimeStamp32 = self.TimeStamp32

            #check for a new log in the log file
            if self.resAll_counter == 2 and self.TimeStamp32 < self.lastTimeStamp32 and self.TimeStamp32 < 100000: ##5000:
                self.baseTimeStamp32 += self.lastTimeStamp32 + 1000000 #gap of 1sec
            #if a new log is detected, don't throw an error
            elif self.lastTimeStamp32 > 0 and abs(self.TimeStamp32-self.lastTimeStamp32) > 1700:
                self.logTime_error = True

            self.resAll_counter = 0
            self.setLog_received = True

        elif cmdid==cGETIMU1: #0x30 #'GET ';
            self.getImu1_counter += 1
        elif cmdid==cGETIMU2:
            self.getImu2_counter += 1

        elif cmdid==cGETMOTP:
            pass
        elif cmdid==cGETMOTR:
            pass
        elif cmdid==cGETMOTY:
            pass

        elif cmdid==cCMDLOG:
            pass

        if True:
            if cmdbyte==None:
                cmdbyte = self.frame.readCmdByte()
            if cmdbyte==255:
                pass
            elif cmdbyte==cCMDBYTE_PidOutData: #CMD LOG  PidData 35
                self.frame.doCmdPidOut(payload)
            elif cmdbyte==cCMDBYTE_Ahrs1Data:#CMD LOG  Ahrs1Data 37
                self.frame.doCmdAhrs1(payload)
            elif cmdbyte==cCMDBYTE_AccGyro1RawData_V2: #CMD LOG  AccGyro1RawData_V2 40
                self.frame.doCmdAccGyro1Raw_V2(payload)
            elif cmdbyte==cCMDBYTE_AccGyro2RawData_V2: #CMD LOG  AccGyro2RawData_V2 41
                self.frame.doCmdAccGyro2Raw_V2(payload)
            elif cmdbyte==cCMDBYTE_AccGyro1Data_V2: #CMD LOG  AccGyro1Data_V2 43
                self.frame.doCmdAccGyro1_V2(payload)
            elif cmdbyte==cCMDBYTE_AccGyro2Data_V2: #CMD LOG  AccGyro2Data_V2 44
                self.frame.doCmdAccGyro2_V2(payload)
            elif cmdbyte==cCMDBYTE_EncoderData: #no. 45
                self.frame.doCmdEncoder(payload)
            elif cmdbyte==cCMDBYTE_Storm32LinkData: #no. 46
                self.frame.doCmdStorm32LinkData(payload)
            elif cmdbyte==cCMDBYTE_PidInData: #no. 50
                self.frame.doCmdPidIn(payload)
            elif cmdbyte==cCMDBYTE_FunctionInputValues: #no. 51
                self.frame.doCmdFunctionInputValues(payload)
            elif cmdbyte==cCMDBYTE_PidIDData: #no. 52
                self.frame.doCmdPidID(payload)
            elif cmdbyte==cCMDBYTE_Storm32LinkData_V2: #no. 53
                self.frame.doCmdStorm32LinkData_V2(payload)
            elif cmdbyte==cCMDBYTE_DebugData: #no. 127
                self.frame.doCmdDebugData(payload)
#XX extract various pieces of information from the log
            elif cmdbyte==cCMDBYTE_ParameterData: #CMD LOG  ParameterData 36
                self.frame.doCmdParameter(payload)
                self.cmdLog36_counter += 1
                paramname_full = str(self.frame.ParameterNameStr.replace(b'\0',b' '), "utf-8")
                paramname = paramname_full.strip()
                if self.frame.ParameterAdr == 65535:
                    self.cmdParameterData.append(paramname)
                    if paramname != '': self.ConfigurationInfoList.append(paramname)
                    if self.cmdParameterData_last == 'STORM32' and paramname[0:3] == 'v2.':
                        self.Storm32FirmwareVersion = int(paramname[1] + paramname[3] + paramname[4])

                    self.cmdParameterData_last = paramname
                else:
                    s = str(self.frame.ParameterAdr) + '\t'+paramname_full + '\t'+str(self.frame.ParameterValue)
                    self.cmdParameterData.append(s)
                    self.ParameterDict[paramname_full] = [self.frame.ParameterAdr,self.frame.ParameterValue,self.frame.ParameterFormat]

                    if paramname == 'CNF_IMU_ORIENT':
                        self.ImuOrientation = self.frame.ParameterValue
                    if paramname == 'STP_IMU2_ORIENT' or paramname == 'CNF_IMU2_ORIENT':
                        self.Imu2Orientation = self.frame.ParameterValue
                    if paramname == 'STP_NTLOGGING':
                        self.NtLogging = self.frame.ParameterValue

            elif cmdbyte==cCMDBYTE_TunnelTx: #no. 47
                self.frame.doCmdTunnelTx(payload)
                self.cmds.append('TunnelTx cmd at time '+str(self.frame.Time/1000)+' ms')
                s = 'cmdTunnelTx: '+str(self.frame.Time/1000)+' ms'
                s+= ', '+str(self.frame.TunnelTxLen)
                s+= ', '+str(self.frame.TunnelTxData)
                self.cmdTunnelTx.append(s)

            elif cmdbyte==cCMDBYTE_AutopilotSystemTime: #no. 49
                self.frame.doCmdAutopilotSystemTime(payload)
                #self.cmds.append('AutopilotSystemTime cmd at time '+str(self.frame.Time/1000)+' ms')
                ts = int(self.frame.UnixTime[0]/1000000)
                s = str(self.frame.Time/1000)+' ms'
                s+= '\t'+str(self.frame.UnixTime[0])
                s+= '\t'+datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d  %H:%M:%S')
                s+= '  '+datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                self.cmdAutopilotSystemTime.append(s)
                if self.AutopilotSystemTime == '':
                    self.AutopilotSystemTime = 'Autopilot System Time:  '
                    self.AutopilotSystemTime += datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d  %H:%M:%S')
                    self.AutopilotSystemTime += datetime.fromtimestamp(ts).strftime('  %H:%M:%S')

            elif cmdbyte==cCMDBYTE_READLOGGERDATETIME: #no. 114
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd READLOGGERDATETIME'
                self.cmds.append(s)
                self.cmdsLogger.append(s)
            elif cmdbyte==cCMDBYTE_WRITELOGGERDATETIME: #no. 115
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd WRITELOGGERDATETIME'
                self.cmds.append(s)
                self.cmdsLogger.append(s)
            elif cmdbyte==cCMDBYTE_STOREMOTORCALIBRATION: #no. 116
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd STOREMOTORCALIBRATION'
                self.cmds.append(s)
                self.cmdsCalibration.append(s)
            elif cmdbyte==cCMDBYTE_READMOTORCALIBRATION: #no. 117
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd READMOTORCALIBRATION'
                self.cmds.append(s)
                self.cmdsCalibration.append(s)
            elif cmdbyte==cCMDBYTE_STOREIMUCALIBRATION: #no. 118
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd STOREIMUCALIBRATION'
                self.cmds.append(s)
                self.cmdsCalibration.append(s)
            elif cmdbyte==cCMDBYTE_READIMUCALIBRATION: #no. 119
                s = str(self.frame.Time/1000)+' ms' + '\t'+'cmd READIMUCALIBRATION'
                self.cmds.append(s)
                self.cmdsCalibration.append(s)

        return True #parser did his job, so tell caller

    #------------------------------------------
    #analyzes the received frame, and appends it if correct
    # stxerror allows the caller to have additional errors considered
    # returns error
    def analyzeAndAppend(self,cmdid,stxerror): #cmdid = 0x80 + cmd + idbyte
        frameError = False
        if cmdid==cTRGALL:

            if self.setLog_received: #a SetLog had been received before, so this is the 2nd TrgAll
                if stxerror: frameError = True
                elif self.frame.error & cNTDATAFRAME_SETLOGERROR > 0: frameError = True
                elif self.frame.error & cNTDATAFRAME_SETMOTERROR > 0: frameError = True
                elif self.logTime_error: frameError = True
                elif self.frame.SetLoggerData_received != 1: frameError = True
                elif self.getImu1_counter != 1: frameError = True
                elif self.getImu2_counter > 1: frameError = True #can be 0 or 1
                elif self.frame.SetMotorAllData_received != 1: frameError = True

                elif self.cmdLog36_counter > 1: frameError = True
                elif self.frame.CmdPidOutData_received > 1: frameError = True
                elif self.frame.CmdAhrs1Data_received > 1: frameError = True
                elif self.frame.CmdAccGyro1RawData_received > 1: frameError = True
                elif self.frame.CmdAccGyro2RawData_received > 1: frameError = True
                elif self.frame.CmdAccGyro1Data_received > 1: frameError = True
                elif self.frame.CmdAccGyro2Data_received > 1: frameError = True
                elif self.frame.CmdEncoderData_received > 1: frameError = True
                elif self.frame.CmdPidInData_received > 1: frameError = True
                elif self.frame.CmdFunctionInputValues_received > 1: frameError = True
                elif self.frame.CmdPidIDData_received > 1: frameError = True
                elif self.frame.CmdStorm32LinkData_received > 1: frameError = True
                elif self.frame.CmdDebugData_received > 1: frameError = True

                if not frameError:
                    self.frame.calculateTime( self.startTimeStamp32-self.baseTimeStamp32 )
                    self.frame.calculateInjectedValues()
                    # this allows appendDataFrame() to do some additional error checks
                    if self.reader.appendDataFrame(self.frame):
                        frameError = True
                    else:
                        self.frameCounts += 1

            self.clearForNextDataFrame()

        if frameError:
            self.errorCounts += 1
        return frameError


###############################################################################
# cNTLogFileReader
# this is the main class to read in a NTLogger data log file
# it generates a number of data lists, for easier handling in the GUI
#-----------------------------------------------------------------------------#

class cNTLogOptions:

    def __init__(self,createFullTraffic=False,sortParameters=False):
        self.createFullTraffic = createFullTraffic
        self.sortParameters = sortParameters
        self.imu1OrientationFlag = 0
        self.imu1OrientationEnum = 0
        self.imu1OrientationX = None
        self.imu2OrientationFlag = 0
        self.imu2OrientationEnum = 0
        self.imu2OrientationX = None
        self.calculationDict = None

    def setCreateFullTraffic(self,flag):
        self.createFullTraffic = flag

    def setSortParameters(self,flag):
        self.sortParameters = flag

    def setCalculationDict(self,dic):
        self.calculationDict = dic

    #called
    def setImu1(self, orientationFlag=1, orientationEnum=0):
        self.imu1OrientationFlag = orientationFlag
        self.imu1OrientationEnum = orientationEnum
        if orientationEnum == 0:
            self.imu1OrientationX = None
        else:
            self.imu1OrientationX = orientationEnum - 1

    def setImu2(self, orientationFlag=1, orientationEnum=0):
        self.imu2OrientationFlag = orientationFlag
        self.imu2OrientationEnum = orientationEnum
        if orientationEnum == 0:
            self.imu2OrientationX = None
        else:
            self.imu2OrientationX = orientationEnum - 1


#this is to report back results to the caller, in additon to traffic, info, data
class cNTLogFileReaderAuxiliaryData:

    def __init__(self):
        self.clear()

    def clear(self):
        self.autopilotSystemTime = ''
        self.imu1Orientation = None
        self.imu2Orientation = None


class cNTLogFileReader:

    def __init__(self):
        self.logVersion = cLOGVERSION_UNINITIALIZED #was a BUG, right? cLOGTYPE_UNINITIALIZED #private


    def readLogFile(self,loadLogThread,fileName,logOptions):
        try:
            F = open(fileName, 'rb')
        except:
            return '','',''

        #this is the header which preludes each data packet, 1+1+4+1+1+1 = 9 bytes, stx = 'R'
        # R(u8) size(u8)(total packet) timestamp(u32) cmd(u8) id(u8) cmdbyte(u8) payload(size-9) (there is no crc)
        headerStruct = struct.Struct('=BBIBBB')
        stx,size,timestamp,cmd,idbyte,cmdbyte = 0,0,0,0,0,0

        frame = cNTLogDataFrame()
        parser = cNTLogParser(frame, self)

        logItemList = cNTLogDataItemList()

        trafficlog = []
        if not logOptions.createFullTraffic:
            trafficlog.append('Only first 500 commands were loaded.\n\n')
        infolog = []
        auxiliaryData = cNTLogFileReaderAuxiliaryData()

        #need to be self so that appendDataFrame() can be called by the parser
        self.datalog = []
        self.datalog.append( logItemList.getNamesAsStr('\t') + '\n' )
        self.datalog.append( logItemList.getUnitsAsStr('\t') + '\n' )

        self.gyroflowlog = []

        cmdset = set() # to record cmd packets of a frame

        trgall_timestamp_last = -1
        trafficlog_counter = 0
        stxerror = False

        byte_counter = 0
        byte_max = QFile(fileName).size()
        byte_percentage = 0
        byte_step = 5

        ##FBytesIO = BytesIO(F.read())  //THIS IS NOT FASTER AT ALL!!
        ##header = FBytesIO.read(9)
        ##payload = FBytesIO.read(size-9)
        frame.setLogVersion(cLOGVERSION_NT_V2) #assume <v0.03 as default
        while 1:
            if loadLogThread.canceled: break

            header = F.read(9)
            if header == '' or len(header) != 9:
                break
            byte_counter += 9
            stxerror = False

            #------------------------------------------
            #check log start line
            # there should be a check that this is the first line!!! #XX
            if header[0:1] == b'H' and header[2:] == b'STORM32':
                size = int(header[1])
                restofheader = F.read(size-9) # read the rest of the log start line
                frame.setLogVersion(cLOGVERSION_NT_V3) #v0.03
                header = F.read(9)

            #------------------------------------------
            #Header, read header data into proper fields
            stx, size, timestamp, cmd, idbyte, cmdbyte = headerStruct.unpack(header)
            if size < 9:
                break;
            if stx != ord('R'):
                cmd, idbyte, cmdbyte = -1, -1, -1
                stxerror = True #NTbus traffic data frame analyzer
            cmdid = 0x80 + cmd + idbyte

            #------------------------------------------
            #Data, read remaining data into proper fields
            payload = F.read(size-9)
            if payload == '' or len(payload) != size-9:
                break
            byte_counter += size-9

            #------------------------------------------
            #read data send with R cmd
            # merged with traffic data frame analyzer
            parser.parse(cmdid, cmdbyte, payload)

            #------------------------------------------
            #NTbus traffic log
            if logOptions.createFullTraffic or trafficlog_counter < 500:
                tl = str(trafficlog_counter)
                ts = str(timestamp)
                while len(ts) < 10: ts = '0'+ts
                trafficlog.append( tl+'\t'+ts+'  ' )

                if cmd==cCMD_RES:   trafficlog.append( 'RES ' )
                elif cmd==cCMD_SET: trafficlog.append( 'SET ' )
                elif cmd==cCMD_GET: trafficlog.append( 'GET ' )
                elif cmd==cCMD_TRG: trafficlog.append( 'TRG ' )
                elif cmd==cCMD_CMD: trafficlog.append( 'CMD ' )
                else: trafficlog.append( '??? ' )

                if idbyte==cID_ALL:
                    trafficlog.append( 'ALL  ' )
                    if cmd==cCMD_TRG:
                        if trgall_timestamp_last >= 0:
                            trafficlog.append( '('+str(timestamp-trgall_timestamp_last)+')' )
                        trgall_timestamp_last = timestamp
                elif idbyte==cID_IMU1: trafficlog.append( 'IMU1 ' )
                elif idbyte==cID_IMU2: trafficlog.append( 'IMU2 ' )
                elif idbyte==cID_MOTA: trafficlog.append( 'MOTA ' )
                elif idbyte==cID_MOTP: trafficlog.append( 'MOTP ' )
                elif idbyte==cID_MOTR: trafficlog.append( 'MOTR ' )
                elif idbyte==cID_MOTY: trafficlog.append( 'MOTY ' )
                elif idbyte==cID_CAMERA: trafficlog.append( 'CAM  ' )
                elif idbyte==cID_LOG:  trafficlog.append( 'LOG  ' )
                elif idbyte==cID_IMU3: trafficlog.append( 'IMU3 ' )
                else: trafficlog.append( '???  ' )

                if stx != ord('R'):
                    trafficlog.append( '\n*******************   ERROR: invalid stx   ****************************************************' )
                elif cmd==cCMD_RES:
                    pass
                elif cmd==cCMD_SET:
                    if idbyte==cID_MOTA:
                        trafficlog.append( '0x'+'{:02X}'.format(frame.Flags) )
                        if frame.Flags & 0x20:
                            trafficlog.append( ' '+str(frame.VmaxPitch)+' '+str(frame.MotPitch) )
                            trafficlog.append( ' '+str(frame.VmaxRoll)+' '+str(frame.MotRoll) )
                            trafficlog.append( ' '+str(frame.VmaxYaw)+' '+str(frame.MotYaw) )
                        else:
                            trafficlog.append( ' '+str(frame.dURawPitch)+' '+str(frame.dURawRoll)+' '+str(frame.dURawYaw) )
                    elif idbyte==cID_CAMERA:
                        if frame.CameraFlags & 0x40:
                            trafficlog.append( '2: '+str(frame.CameraCmd2)+' '+str(frame.CameraValue2) )
                        else:
                            trafficlog.append( '1: '+str(frame.CameraCmd)+' '+str(frame.CameraValue)+' '+str(frame.CameraPwm) )
                    elif idbyte==cID_LOG:
                        trafficlog.append( str(parser.TimeStamp32) )
                        if parser.TimeStamp32 > 0:
                            trafficlog.append( ' ('+str(parser.TimeStamp32-parser.lastTimeStamp32)+')' )
                            trafficlog.append( ' '+str((parser.TimeStamp32-parser.startTimeStamp32)/1000)+' ms' )
                elif cmd==cCMD_GET:
                    pass
                elif cmd==cCMD_TRG:
                    pass
                elif cmd==cCMD_CMD:
                    trafficlog.append( str(cmdbyte) )
                    if cmdbyte==cCMDBYTE_ParameterData:
                        if frame.ParameterAdr==65535:
                            trafficlog.append( '\t'+str(frame.ParameterNameStr, "utf-8") )
                        else:
                            trafficlog.append( '\t'+str(frame.ParameterAdr) )
                            trafficlog.append( '\t'+str(frame.ParameterNameStr.replace(b'\0',b' '), "utf-8") )
                            trafficlog.append( '\t'+str(frame.ParameterValue) )
                    ''' we don't really need it, was for debugging
                    if cmdbyte==cCMDBYTE_READLOGGERDATETIME:
                        trafficlog.append( '\t!!!!!!!!!!!!!!!!!!!!   RTC READ   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' )
                    if cmdbyte==cCMDBYTE_WRITELOGGERDATETIME:
                        trafficlog.append( '\t!!!!!!!!!!!!!!!!!!!!   RTC WRITE   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' )
                    '''

                trafficlog.append( '\n' )
                trafficlog_counter += 1

            #------------------------------------------
            #NTbus traffic data frame analyzer
            if cmd==cCMD_CMD:
                cmdset.add(cmdbyte)

            frameError = parser.analyzeAndAppend(cmdid, stxerror)

            if frameError:
                if( logOptions.createFullTraffic or trafficlog_counter<500 ):
                    trafficlog.append( '*******************   ERROR: lost frame(s)   ****************************************************\n' )

            if 80*(byte_counter/byte_max) > byte_percentage:
                loadLogThread.emitProgress(byte_percentage)
                byte_percentage += byte_step
        #end of while 1:

        F.close();
        loadLogThread.emitProgress(80)
        #if not (logOptions.createFullTraffic or trafficlog_counter<500 ): trafficlog.append( '...\n' )
        if not logOptions.createFullTraffic: trafficlog.append( '...\n' )
        trafficlog.append( '\nFRAME COUNTS: '+str(parser.frameCounts) + '\n' )
        trafficlog.append( 'ERROR COUNTS: '+str(parser.errorCounts) + '\n' )
        trafficlog.append( '\nAUTOPILOT_SYSTEMTIME COUNTS: '+str(len(parser.cmdAutopilotSystemTime))+ '\n' )
        trafficlog.append( 'TUNNEL_TX COUNTS: '+str(len(parser.cmdTunnelTx))+ '\n' )
        trafficlog.append( 'RTC READ&WRITE COUNTS: '+str(len(parser.cmdsLogger))+ '\n' )

        '''old way of list
        infolog.append( 'PARAMETERS:\n\n' )
        for sss in parser.cmdParameterData:
            infolog.append( '    '+sss+'\n' )
        infolog.append( '\n\n' )
        '''

        infolog.append( 'CONFIGURATION INFO:\n' ) #only one '\n' here
        for sss in parser.ConfigurationInfoList:
            if sss.find('MODULE') != -1: infolog.append('\n')
            if sss.find('STORM32') != -1: infolog.append('\n')
            if sss.find('ACC1') != -1: infolog.append('\n')
            infolog.append( '    '+sss+'\n' )
        infolog.append( '\n\n' )

        infolog.append( 'PARAMETERS:\n\n' )
        if logOptions.sortParameters:
            kkk = sorted(parser.ParameterDict.keys())
        else:
            kkk = parser.ParameterDict.keys()
        #for sss in sorted(parser.ParameterDict.keys()):
        for sss in kkk:
            if sss[:3] == 'NU_': continue
            vvv = parser.ParameterDict[sss]
            infolog.append( '    '+sss+' ('+str(vvv[0])+')\t'+str(vvv[1])+'\n' )
        infolog.append( '\n\n' )

        infolog.append( 'IMU ORIENTATIONS:\n\n' )
        if parser.ImuOrientation != None:
            infolog.append( '    Imu Orientation: '+str(parser.ImuOrientation)+'\n' )
        else:
            infolog.append( '    Imu Orientation: '+'None'+'\n' )
        if parser.Imu2Orientation != None:
            infolog.append( '    Imu2 Orientation: '+str(parser.Imu2Orientation)+'\n' )
        else:
            infolog.append( '    Imu2 Orientation: '+'None'+'\n' )
        infolog.append( '\n\n' )

        infolog.append( 'NT LOGGING:\n\n' )
        if parser.NtLogging == None or parser.Storm32FirmwareVersion == None:
            infolog.append( '    setting unknown\n' )
        elif parser.Storm32FirmwareVersion < 256: #old NtLoggig parameter
            NtLoggingOld = ['off','basic','basic + pid','basic + accgyro','basic + accgyro_raw','basic + pid + accgyro','basic + pid + ag_raw','full']
            infolog.append( '    '+str(parser.NtLogging)+' = '+NtLoggingOld[parser.NtLogging]+'\n' )
        else: #new NtLogging mask
            if parser.NtLogging == 0:
                infolog.append( '    '+str(parser.NtLogging)+' = off\n' )
            else:
                s = ''
                if parser.NtLogging >= 256-1: s = 'full = '
#                if parser.NtLogging >= 64-1: s = 'full = '
                if parser.NtLogging & 1: s += 'Basic, '
                if parser.NtLogging & 2: s += 'Acc + Ayro raw, '
                if parser.NtLogging & 4: s += 'PID In, '
                if parser.NtLogging & 64: s += 'PID I D, '
                if parser.NtLogging & 8: s += 'PID Out, '
                if parser.NtLogging & 16: s += 'Acc + Gyro, '
                if parser.NtLogging & 32: s += 'Inputs, '
                if parser.NtLogging & 128: s += 'STorM32 Link, '
                infolog.append( '    '+str(parser.NtLogging)+' = '+s[:-2]+'\n' )
        infolog.append( '\n' )
        cmdset.difference_update([1,2,3,4,36,47,48,49,114,115,116,117,118,119])
        if len(cmdset) > 0:
            for cmdbyte in cmdset:
                s = '    CMD LOG  ' + '{:<3d}'.format(cmdbyte) + '  ' + getCmdByteStr(cmdbyte) + '\n'
                infolog.append( s )
            infolog.append( '\n\n' )

        '''we don't really need it, only first is relevant
        infolog.append( 'AUTOPILOT_SYSTEMTIME COUNTS: '+str(len(parser.cmdAutopilotSystemTime))+ '\n' )
        infolog.append( 'AUTOPILOT_SYSTEMTIME:\n\n' )
        if len(parser.cmdAutopilotSystemTime) == 0:
            infolog.append( '    none\n' )
        else:
            for sss in parser.cmdAutopilotSystemTime:
                infolog.append( '    '+sss+'\n' )
        infolog.append( '\n\n' )
        '''

        infolog.append( 'SPECIAL COMMANDS:\n\n' )
        if len(parser.cmds) == 0:
            infolog.append( '    none\n' )
        else:
            for sss in parser.cmds:
                infolog.append( '    '+sss+'\n' )
        infolog.append( '\n\n' )

        auxiliaryData.autopilotSystemTime = parser.AutopilotSystemTime
        auxiliaryData.imu1Orientation = parser.ImuOrientation
        auxiliaryData.imu2Orientation = parser.Imu2Orientation

        if loadLogThread.canceled:
            trafficlog = []
            infolog = []
            auxiliaryData.clear()
            self.datalog = []
        self.logVersion = frame.getLogVersion()
        return trafficlog, self.datalog, infolog, auxiliaryData, self.gyroflowlog

    #this is called by the parser
    # returns a bool, True if error occured
    def appendDataFrame(self,_frame):
        self.datalog.append( _frame.getDataLine() )
        self.gyroflowlog.append( _frame.getGyroFlowDataLine() )
        return False

    def getLogVersion(self):
        return self.logVersion
