#!/usr/bin/env python
#*******************************************************
# Copyright (c) OlliW42, STorM32 project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#*******************************************************
whichUiToUse = 'ow_py'
#whichUiToUse = 'py'
#whichUiToUse = 'ui'


ApplicationStr = "NT DataLogger"
VersionStr = "22. Oct. 2023 v0.51b"
IniFileStr = "./NTLoggerTool.ini"


#comments/todos:
# - hsb = self.wDataText.horizontalScrollBar()
#   hsb.setValue(v)
#   doesn't work then wDataText is not visible
#
# - with yAR off, and if a [A] is done in the plot, when plot is autoranging and yAR off is ignored??
#   does autoRange() also enable auto range?
#   seems so, a disableAutoRange() seems to do the trick
#
# - the whole date version thing needs to be revisted, logItemList should also adapt to NT log file version
#   circumvented currently, by simply adding the required fields, and to set the unused ones to zero
#XX

import sys
import struct
from math import sqrt, sin, pi, atan2
from copy import deepcopy
import re
import subprocess
import time

from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort, QtNetwork
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QFile, Qt, QSettings, QTimer, QIODevice, QMutex
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QColorDialog, QDialog, QWidget,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QToolButton,
                             QStyleFactory, QStyle, QListWidgetItem, QTreeWidgetItem, QComboBox)
from PyQt5.QtGui import QPalette, QColor, QFont, QFontInfo, QFontMetrics, QFontDatabase, QDoubleValidator
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtNetwork import (QTcpSocket, QUdpSocket)

#pyuic5 input.ui -o output.py
if( whichUiToUse=='ow_py' ):
    import NTLoggerTool_ui_ow
    wMainWindow = NTLoggerTool_ui_ow.Ui_wWindow
elif( whichUiToUse=='py' ):
    import NTLoggerTool_ui
    wMainWindow = NTLoggerTool_ui.Ui_wWindow
else:
    from PyQt5.uic import loadUiType
    wMainWindow, _ = loadUiType('NTLoggerTool_ui.ui')

import numpy as np
from io import StringIO, BytesIO #this is needed to make np.loadtxt to work
import pyqtgraph as pg

#import cv2

from owSerial_v01 import cRingBuffer, cSerialPortComboBox, cSerialStream
from owNTLoggerObjects_v042 import (cLogDataItemTranslator, cLogDataItemList,
                                    cDATATYPE_FLOAT, cLOGTYPE_UNINITIALIZED, cLOGVERSION_UNINITIALIZED)
from owNTLog_v049 import (cNTLogDataItemList, cNTLogSerialDataFrame,
                          cNTLogParser, cNTLogFileReader, cNTLogOptions, cNTLogFileReaderAuxiliaryData)


###################################################################
# def __init__(self):
#   super() calls a method of the parent class
#   super(cWorkerThread, self).__init__()
# https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
#   super(self.__class__, self).__init__() #this is to call the init of the paranet class
# http://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods
#   super().__init__() #this is IMHO the best

###################################################################
# general stuff
###################################################################

def trimStrWithCharToLength(s, len_, c):
    while len(s)<len_: s = s + c
    return s

def strwt(s): return str(s)+"\t"

def strwn(s): return str(s)+"\n"

def int_to_u16(i):
    if i<0: i += 65536
    if i>65536-1: i = 65536-1
    return i


###############################################################################
# cLogDataItemTranslator
# cStorm32GuiLogItemTranslator(cLogItemTranslator)
# helper class to translate data field names from various source files to
# the standard NTLogger data field names
#-----------------------------------------------------------------------------#
class cStorm32GuiLogDataItemTranslator(cLogDataItemTranslator):

    storm32GuiLogTranslateDict = {
        'Gx':'gx1', 'Gy':'gy1', 'Gz':'gz1',
        'Rx':'Rx1', 'Ry':'Ry1', 'Rz':'Rz1',
        'AccAmp':'AccAmp1', 'AccConf':'AccConf1',
        'Pitch':'Imu1Pitch', 'Roll':'Imu1Roll', 'Yaw':'Imu1Yaw',
        'Pitch2':'Imu2Pitch', 'Roll2':'Imu2Roll', 'Yaw2':'Imu2Yaw',
        'PCntrl':'PIDPitch', 'RCntrl':'PIDRoll', 'YCntrl':'PIDYaw',
        'PEnc':'EncPitch', 'REnc':'EncRoll', 'YEnc':'EncYaw',
        }

    def translate(self, _name):
        if _name in self.storm32GuiLogTranslateDict:
            return self.storm32GuiLogTranslateDict[_name]
        return _name


###############################################################################
# cNTImuOrientation
# helper class to handle imu orientatiosn and rotations
#-----------------------------------------------------------------------------#

class cNTImuOrientation:

    def __init__(self):
        self.orientationFlagList = [
            'off','auto','fixed'
            ]
        self.orientationList = [
            'unknown',
            'no.0: z0° +x +y +z',
            'no.1: z90° -y +x +z',
            'no.2: z180° -x -y +z',
            'no.3: z270° +y -x +z',
            'no.4: x0° +y +z +x',
            'no.5: x90° -z +y +x',
            'no.6: x180° -y -z +x',
            'no.7: x270° +z -y +x',
            'no.8: y0° +z +x +y',
            'no.9: y90° -x +z +y',
            'no.10: y180° -z -x +y',
            'no.11: y270° +x -z +y',
            'no.12: -z0° +y +x -z',
            'no.13: -z90° -x +y -z',
            'no.14: -z180° -y -x -z',
            'no.15: -z270° +x -y -z',
            'no.16: -x0° +z +y -x',
            'no.17: -x90° -y +z -x',
            'no.18: -x180° -z -y -x',
            'no.19: -x270° +y -z -x',
            'no.20: -y0° +x +z -y',
            'no.21: -y90° -z +x -y',
            'no.22: -y180° -x -z -y',
            'no.23: -y270° +z -x -y']


###############################################################################
# cNTSerialReaderThread
# this is the main class to read NT bus data via a serial port
# it generates a data line for each completely received frame
# is a worker thread to avoid GUI blocking
#-----------------------------------------------------------------------------#
class cNTSerialReaderThread(QThread):

    newSerialDataAvailable = pyqtSignal()

    def __init__(self, _serial):
        super().__init__()
        self.canceled = True

        self.serial = _serial

        self.dataline_local = None
        self.dataline = None
        self.mutex = QMutex() #to protect self.dataline
        self.baseTime = 0
        self.lastChar = b''

    def __del__(self):
        pass #XX ??? now rasies RuntimeError ??? self.wait()

    def clear(self):
        self.dataline_local = None
        self.dataline = None
        self.baseTime = 0

    def run(self):
        self.canceled = False
        self.runCallback()

    def cancel(self):
        self.canceled = True
        self.cancelCallback()

    def cancelIfRunning(self):
        if self.isRunning(): self.cancel()

    def cancelCallback(self):
        pass

    #helper function, called before thread is started
    def openSerial(self, currentport):
        self.serial.open(currentport)

    #helper function, called after thread is stopped
    def closeSerial(self):
        self.serial.close()

    def runCallback(self):
        #self.port.open(QIODevice.ReadWrite) #this must be done in Main!!
        if not self.serial.isValid(): return
        logItemList = cNTLogDataItemList()
        self.dataline_local = ''
        if self.baseTime == 0:
            self.dataline_local = logItemList.getNamesAsStr('\t') + '\n'
            self.dataline_local += logItemList.getUnitsAsStr('\t') + '\n'
        self.dataline = ''
        self.time = self.baseTime
        frame = cNTLogSerialDataFrame(self)
        parser = cNTLogParser(frame, self, self.baseTime)
        self.lastChar = b''
#        timeOfLastRead = time.clock()
        LookAhead = 0
        timeOfLastRead = 0
        while 1:
            if self.canceled: break
            LookAhead = 512
#            timeNow = time.clock() #time in seconds
#            if timeNow-timeOfLastRead > 0.25: LookAhead = 0
            if timeOfLastRead > 3: LookAhead = 0
            timeOfLastRead += 1

            while self.serial.bytesAvailable() > LookAhead: #digest all data accumulated since the last call
#                timeOfLastRead = time.clock()
                timeOfLastRead = 0
                b = self.readByte()
                c = int(b[0])
                if parser.parse(c): #this allows the parser to skip it, for NT e.g. if c<128: continue #this can't be a cmdid
                    parser.analyzeAndAppend(c, 0) #calls reader.appendDataFrame() for each parsed line
                self.time = frame.Time

            if len(self.dataline_local) > 0:
                self.mutex.lock()
                self.dataline += self.dataline_local #this is so that nothing can be missed
                self.mutex.unlock()
                self.dataline_local = ''
                self.emitNewSerialDataAvailable() #it has then 100ms time to process, hopefully enough
                self.baseTime = self.time

            self.msleep(100)

        self.baseTime += 1000000 #add 1sec to make a gap

    def readByte(self):
        if self.lastChar != b'':
            b = self.lastChar
            self.lastChar = b''
        else:
            b = self.serial.readOneByte()
        return b

    #this is called by the NTLogDataFrame class, so that can backtrack char in case of a STX byte
    # res is forced to have the desired length, but is then padded with nonsense
    def readPayload(self, length):
        res = b''
        err = False
        for i in range(length):
            if self.lastChar != b'': #skip, but fill
                res += b'\x7e'
                err = True
            else:
                b = self.serial.readOneByte()
                if int(b[0]) >= 128: #this is a cmdid
                    self.lastChar = b
                    b = b'\x7f'
                    err = True
                res += b
        return (res,err)

    #this is called by the parser
    # returns a bool, True if error occured
    def appendDataFrame(self, frame):
        #here one can do some more error checks
        dataError = False
        if not frame.isValid(): dataError = True #if _frame.State>100: dataError = True
        if not dataError:
            self.dataline_local += frame.getDataLine()
        return dataError

    def emitNewSerialDataAvailable(self):
        self.newSerialDataAvailable.emit()

    #this is called by main, serialReaderThreadNewDataAvailable()
    def getDataLine(self):
        self.mutex.lock()
        dataline = self.dataline
        self.dataline = ''
        self.mutex.unlock()
        return dataline

    def getLogType(self):
        return cLOGTYPE_NTLOGGER

    def getLogVersion(self):
        return cNTLOGVERSION_LATEST



###############################################################################
# cLogDataContainer
# class to hold and maintain the data
#  traffic and data are actually stored in QT widget objects
#-----------------------------------------------------------------------------#
##already defined cLOGVERSION_UNINITIALIZED = 0 #is identical to cLOGVERSION_UNINITIALIZED, version handling is not yet good

#already defined cLOGTYPE_UNINITIALIZED = 0
cLOGTYPE_NTLOGGER = 1       #log file created by NTLogger, or by serialReader
cLOGTYPE_STORM32GUI = 2     #log file created by STorM32's GUI o323BGCTool
cLOGTYPE_ASCII = 3          #ascii log file
##XX ??? cLOGTYPE_GENERICASCII = 32 #.dat,.txt,.csv
#not used cLOGTYPE_NTIMUDIRECT = 4    #log file created by direct logging of NT Imu

#not used cLOGTYPE_SERIALDIRECT = 5   #log file created by direct logging of serial adapter

cLOGSOURCE_UNINITIALIZED = 0
cLOGSOURCE_LOAD = 1         #data has be read from a log file, triggered by Load
cLOGSOURCE_RECORD = 2       #data has be obtained from recording, triggered by RecStart

class cLogDataContainer:

    def __init__(self, _wTrafficText, _wInfoText, _wAutopilotSystemTime, 
                    _wImu1Orientation, _wImu2Orientation,
                    _wFftLengthComboBox=None):
        self.wTrafficText = _wTrafficText
        self.wInfoText = _wInfoText
        self.wAutopilotSystemTime = _wAutopilotSystemTime
        self.wImu1Orientation = _wImu1Orientation
        self.wImu2Orientation = _wImu2Orientation
        self.wFftLengthComboBox = _wFftLengthComboBox

        self.clear()

    def clear(self):
        self.fileName = ''
        self.wTrafficText.setPlainText('')
        self.wInfoText.setPlainText('')
#        self.wInfoText.horizontalScrollBar().setValue(0)
        self.wAutopilotSystemTime.setText('')
        self.auxiliaryData = cNTLogFileReaderAuxiliaryData() #we need to keep the original imu orientation data
        self.data = ''
        self.logItemList = cNTLogDataItemList() #default itemlist
        self.logType = cLOGTYPE_UNINITIALIZED
        self.logVersion = cLOGVERSION_UNINITIALIZED
        self.logSource = cLOGSOURCE_UNINITIALIZED
        self.recordOn = False
        self.initializeNpArrayAndPlotView()
        self._dT = None #0.001 #0.0015

    def initializeNpArrayAndPlotView(self, length=1):
        if length < 0: length = 1
        self._npArrayWidth = len(self.logItemList.list)
        self._npArray = np.zeros((length,self._npArrayWidth))
        self._npArrayPtr = 0
        self._npArrayStep = 1
        self._npPlotView = self._npArray[self._npArrayPtr,:]

    #is called in main by serialReaderThreadNewDataAvailable(), which is emitted by the serialReaderThread
    def appendDataLine(self, dataline):
#        hsb = self.wInfoText.horizontalScrollBar()
#        v = hsb.value()
###XX        self.wInfoText.appendPlainText( dataline[:-1] )
#        hsb.setValue(v)
        for line in dataline.split('\n'):
            #print("!"+line+"!")
            if '[' in line or ']' in line or 'Time' in line: continue # to avoid calling fromstring()
            try:
                a = np.fromstring( line, sep = '\t' ) # this creates now a deprecatedWarning!
            except:
                continue
            if a.size != self._npArrayWidth: continue #something is wrong with that line
            a[0] *= 0.001 #convert time from us to ms
            self._npArray[self._npArrayPtr,:] = a
            self._npArrayPtr += 1
            if self._npArray.shape[0] < 1000:
                self.initializeNpArrayAndPlotView(667*60*5)  #*30 #30 min
            if self._npArrayPtr >= self._npArray.shape[0]:
                tmp = self._npArray
                self._npArray = np.empty( (2*self._npArray.shape[0], self._npArray.shape[1]) )
                self._npArray[:tmp.shape[0],:] = tmp
                
        #print("!"+dataline+"!")
        self.data += dataline

    def hasData(self):
        #in some functions I had before
        # if self.dataContainer.logSource == cLOGSOURCE_UNINITIALIZED: return
        # if self.dataContainer.logType == cLOGTYPE_UNINITIALIZED: return
        #is this always consistent with npArray=0 ??? seems so, so far
        return self._npArrayPtr

    #sets some metrics for the log data
    # is called in loadLogFileDone() 
    ### HOW TO HANDLE SERIAL DATA STREAM ???? serialReaderThreadNewDataAvailable() also sets dataContainer data
    # wGraphFftLength is a reference to a combobox widget, which holds FFT sample legths
    def setLogType(self):
        self._npArrayStep = 1 #take every sample/data frame
        if self.logType == cLOGTYPE_NTLOGGER:
            self._dT = 0.0015
        elif self.logType == cLOGTYPE_STORM32GUI:
            self._dT = 0.0450  #measured: ca 47ms
        else:
            self._dT = 0.0015
        #if plotType == '8khz acc fft':
        #    self._npArrayStep = 2
        #    self._dT = 0.003
        if self.wFftLengthComboBox:
            if self._dT == 0.001:
                self.wFftLengthComboBox.setItemText(0, '2048/2.0s')
                self.wFftLengthComboBox.setItemText(1, '1024/1.0s')
                self.wFftLengthComboBox.setItemText(2, '512/0.51s')
                self.wFftLengthComboBox.setItemText(3, '256/0.26s')
            elif self._dT == 0.045:
                self.wFftLengthComboBox.setItemText(0, '2048/92s')
                self.wFftLengthComboBox.setItemText(1, '1024/46s')
                self.wFftLengthComboBox.setItemText(2, '512/23s')
                self.wFftLengthComboBox.setItemText(3, '256/11s')
            else: #self._dT == 0.0015
                self.wFftLengthComboBox.setItemText(0, '2048/3.1s')
                self.wFftLengthComboBox.setItemText(1, '1024/1.5s')
                self.wFftLengthComboBox.setItemText(2, '512/0.77s')
                self.wFftLengthComboBox.setItemText(3, '256/0.38s')

    def getNpPlotView(self, plotCount=2): #plotCount is the number of displayed curves
        if self._npArrayPtr:
            n = 0
            if self.recordOn:
                n = self._npArrayPtr - self.maxPlotRangeWhileRecording(plotCount)
                if n < 0: n = 0
            return self._npArray[n:self._npArrayPtr:self._npArrayStep,:] #this is a view on the buffer!!!
        return None #self._npPlotView #self._npArray[self._npArrayPtr,:]

    def setRecordOn(self, flag):
        self.recordOn = flag
        if flag and not self.hasData():
            #print("FIRST RECORD ON")
            self.data = ''
            self.wTrafficText.setPlainText('traffic not available in this log file')
            self.wInfoText.setPlainText('info not available in this log file')

    def dT(self):
        if self._dT == None: self.setLogType() #try to determine a useful dT
        return self._dT #0.0015 * self._npArrayStep  #XX 0.0015

    def maxPlotRangeWhileRecording(self, plotCount):
        if plotCount < 2: plotCount = 2
##BUG: gives a float, must be integer:        return 20000/(2*plotCount) #40000 #this is 15sec with 8kHz
        return int(20000/(2*plotCount)) #40000 #this is 15sec with 8kHz #in python3 division always returns float

    def getMaxTime(self):
        if self._npArrayPtr:
            return self._npArray[self._npArrayPtr-1,0]
        return 0.0

    def getSTorM32FirmwareVersion(self):
        t = self.wTrafficText.toPlainText()[0:2000] #the plain text can contain '\0'!!
        m = re.search( r'STORM32[\0\s]*\d+\s+\d+\s+CMD LOG\s+36\s+([ \w\.]+)', t )
        if m == None:
            return 'vx.xx'
        else:
            return m.group(1)


###############################################################################
# cWorkerThread
# worker thread to avoid GUI blocking when loading/saving files
#-----------------------------------------------------------------------------#
class cWorkerThread(QThread):

    progress = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.progressValue = 0
        self.canceled = False

    def __del__(self):
        pass #XX ??? now rasies RuntimeError ??? self.wait()

    def run(self):
        self.progressValue = 0
        self.canceled = False
        self.runCallback()

    def cancel(self):
        self.canceled = True
        self.cancelCallback()

    def runCallback(self):
        pass

    def cancelCallback(self):
        pass

    def emitProgress(self, progress_value):
        self.progressValue = progress_value
        self.progress.emit()

    def startProgress(self, _step, _length):
        self.progressValue = 0
        self.progressValue_step = _step
        self.index = 0
        self.percentage_step = _length*(_step/100)
        self.percentage = self.percentage_step
        self.emitProgress(0)

    def updateProgress(self):
        self.index += 1
        if self.index > self.percentage:
            self.percentage += self.percentage_step
            self.progressValue += self.progressValue_step
            self.emitProgress(self.progressValue)


class cLoadLogThread(cWorkerThread):

    def __init__(self):
        super().__init__()

        self.auxiliaryData = cNTLogFileReaderAuxiliaryData()
        self.setLoadFile('', None)

        self.isRecalculate = None

    def setLoadFile(self, fileName, options): #this is for starting loading a file
        self.fileName = fileName
        self.logOptions = options
        self.traffic = ''
        self.info = ''
        self.auxiliaryData.clear()
        self.data = ''
        self.gyroflowData = ''
        self.npArray = np.zeros((0,0)) #None
        self.logItemList = None
        self.logType = cLOGTYPE_UNINITIALIZED
        self.logVersion = cLOGVERSION_UNINITIALIZED
        
        self.isRecalculate = False

    def setRecalculate(self, dataContainer, options): #this is for starting recalculation
        #self.fileName = fileName #not needed
        self.logOptions = options #needed, but not changed
        #self.traffic = '' #not needed
        #self.info = '' #not needed
        self.auxiliaryData = dataContainer.auxiliaryData #needed, but not changed
        self.data = dataContainer.data #needed, but not changed
        #self.gyroflowData #not needed
        self.npArray = np.zeros((0,0)) #None
        self.logItemList = dataContainer.logItemList #needed, but not changed
        self.logType = dataContainer.logType #needed, but not changed
        #self.logVersion = cLOGVERSION_UNINITIALIZED #not needed

        self.isRecalculate = True

    def isNTLog(self):
        if self.fileName.lower().endswith('.ntlog') or self.fileName.lower().endswith('.log'): return True
        return False

    def runCallback(self):
        if self.logOptions == None: exit(1) #should never happen
        if self.isRecalculate:
            self.recalculateNTLoggerFile()
        elif self.isNTLog():
            self.loadNTLoggerFile()
        else:
            self.loadSTORM32GUIorASCIIFile()

    def recalculateNTLoggerFile(self):
        self.emitProgress(80)
        self.createNpArray(2, 0)

    def loadNTLoggerFile(self):
        self.emitProgress(0)
        logReader = cNTLogFileReader()
        traffic, data, info, auxiliaryData, gyroflowData = logReader.readLogFile(self, self.fileName, self.logOptions)
        self.traffic = ''.join(traffic)
        self.info = ''.join(info)
        self.auxiliaryData = auxiliaryData
        self.data = ''.join(data)
        self.gyroflowData = ''.join(gyroflowData)
        self.logItemList = cNTLogDataItemList()
        self.logType = cLOGTYPE_NTLOGGER
        self.logVersion = logReader.getLogVersion()
        self.createNpArray(2, 0)

    def loadSTORM32GUIorASCIIFile(self): #this actually reads all sorts of ascii text files
        try:
            F = open(self.fileName, 'r')
        except IOError:
            return #pass
        data = []
        sep = None
        oldTimeIndex = -1
        first = True
        reLine = re.compile(r'^[0-9.+-E\s,]+$')
        isSTorM32DataDisplay = False
        STorM32DataDisplayHeader = r'^i\tTime\tMillis\tGx\tGy\tGz\tRx\tRy\tRz\tAccAmp\tAccConf\tPitch\tRoll\tYaw\tPCntrl\tRCntrl\tYCntrl\tPitch2\tRoll2\tYaw2'
        isSTorM32DataDisplayFoc = False
        STorM32DataDisplayHeaderFoc = r'^i\tTime\tMillis\tRx\tRy\tRz\tAccAmp\tAccConf\tPitch\tRoll\tYaw\tPCntrl\tRCntrl\tYCntrl\tPitch2\tRoll2\tYaw2\tPEnc\tREnc\tYEnc\tState'
        isSTorM32NtLiveRecord = False
        STorM32NtLiveRecordHeader = r'^Time\tImu1rx\tImu1done\tPIDdone\tMotdone\tImu2rx\tImu2done\tLogdone\tLoopdone\tState\tStatus\tStatus2\tErrorCnt\tVoltage'
        for line in F:
            line = line.strip()
            if first:
                if re.search(r',', line): sep = ','
                if re.search(r'[a-zA-Z]', line): #this is a header line
                    line = '\t'.join(line.split(sep)) #this is MUCH faster than a regex!  re.sub(r'[\s,]+', '\t', line)
                    if re.search(STorM32DataDisplayHeader, line):
                        isSTorM32DataDisplay = True
                        logItemList = cNTLogDataItemList(cStorm32GuiLogDataItemTranslator())
                    elif re.search(STorM32DataDisplayHeaderFoc, line):
                        isSTorM32DataDisplayFoc = True
                        logItemList = cNTLogDataItemList(cStorm32GuiLogDataItemTranslator())
                    elif re.search(STorM32NtLiveRecordHeader, line):
                        isSTorM32NtLiveRecord = True
                        logItemList = cNTLogDataItemList()
                    else:
                        logItemList = cLogDataItemList()
#                        logItemList = cNTLogDataItemList() #this is ok, all 'know' fields are digested, all 'unknown' fields are appended
                    logItemList.setFromStr(line, '', cDATATYPE_FLOAT, cDATATYPE_FLOAT, '\t')
                    oldTimeIndex = logItemList.swapTimeToZeroIndex()
                    data.append( logItemList.getNamesAsStr('\t') + '\n' )
            if reLine.search(line):
                d = line.split(sep)
                if isSTorM32DataDisplay:
                    d[6]  = '{:.4f}'.format( 0.0001 * float(d[6]) )#Rx
                    d[7]  = '{:.4f}'.format( 0.0001 * float(d[7]) )#Ry
                    d[8]  = '{:.4f}'.format( 0.0001 * float(d[8]) )#Rz
                    d[9]  = '{:.4f}'.format( 0.0001 * float(d[9]) )#AccAmp
                    d[10] = '{:.4f}'.format( 0.0001 * float(d[10]) ) #AccConf
                    d[11] = '{:.2f}'.format( 0.01 * float(d[11]) ) #Pitch
                    d[12] = '{:.2f}'.format( 0.01 * float(d[12]) ) #Roll
                    d[13] = '{:.2f}'.format( 0.01 * float(d[13]) ) #Yaw
                    d[14] = '{:.2f}'.format( 0.01 * float(d[14]) ) #PCntrl
                    d[15] = '{:.2f}'.format( 0.01 * float(d[15]) ) #RCntrl
                    d[16] = '{:.2f}'.format( 0.01 * float(d[16]) ) #YCntrl
                    d[17] = '{:.2f}'.format( 0.01 * float(d[17]) ) #Pitch2
                    d[18] = '{:.2f}'.format( 0.01 * float(d[18]) ) #Roll2
                    d[19] = '{:.2f}'.format( 0.01 * float(d[19]) ) #Yaw2
                if isSTorM32DataDisplayFoc:
                    d[3]  = '{:.4f}'.format( 0.0001 * float(d[3]) )#Rx
                    d[4]  = '{:.4f}'.format( 0.0001 * float(d[4]) )#Ry
                    d[5]  = '{:.4f}'.format( 0.0001 * float(d[5]) )#Rz
                    d[6]  = '{:.4f}'.format( 0.0001 * float(d[6]) )#AccAmp
                    d[7] = '{:.4f}'.format( 0.0001 * float(d[7]) ) #AccConf
                    d[8] = '{:.2f}'.format( 0.01 * float(d[8]) ) #Pitch
                    d[9] = '{:.2f}'.format( 0.01 * float(d[9]) ) #Roll
                    d[10] = '{:.2f}'.format( 0.01 * float(d[10]) ) #Yaw
                    d[11] = '{:.2f}'.format( 0.01 * float(d[11]) ) #PCntrl
                    d[12] = '{:.2f}'.format( 0.01 * float(d[12]) ) #RCntrl
                    d[13] = '{:.2f}'.format( 0.01 * float(d[13]) ) #YCntrl
                    d[14] = '{:.2f}'.format( 0.01 * float(d[14]) ) #Pitch2
                    d[15] = '{:.2f}'.format( 0.01 * float(d[15]) ) #Roll2
                    d[16] = '{:.2f}'.format( 0.01 * float(d[16]) ) #Yaw2
                    d[17] = '{:.2f}'.format( 0.01 * float(d[17]) ) #Pitch2
                    d[18] = '{:.2f}'.format( 0.01 * float(d[18]) ) #Roll2
                    d[19] = '{:.2f}'.format( 0.01 * float(d[19]) ) #Yaw2
                data.append( '\t'.join(d) + '\n'  ) #this is MUCH faster than a regex!!!!
#XX do a check that the line is complete!!!
            first = False #only check first line
        F.close()
        self.auxiliaryData.clear() #should have been done already, but can't hurt
        self.traffic = 'traffic not available in this log file'
        self.info = 'info not available in this log file'
        self.data = ''.join(data)
        self.gyroflowData = ''
        self.logItemList = logItemList
        if isSTorM32DataDisplay or isSTorM32DataDisplayFoc:
            self.logType = cLOGTYPE_STORM32GUI
        elif isSTorM32NtLiveRecord:
            self.logType = cLOGTYPE_NTLOGGER #this should not be different from a NT Logger log
        else:
            self.logType = cLOGTYPE_ASCII
        self.logVersion = cLOGVERSION_UNINITIALIZED #is irrelevant here since its not a NT Logger log
        self.createNpArray(1, oldTimeIndex)

    def getImuPermutSign(self, orientation):
        imuOrientations = cNTImuOrientation()
        s = imuOrientations.orientationList[orientation+1]
        l = s.split(' ')[2:]
        permut = []
        signs = []
        for i in range(3):
            if l[i][1] == 'x': permut.append(0)
            if l[i][1] == 'y': permut.append(1)
            if l[i][1] == 'z': permut.append(2)
            if l[i][0] == '+': signs.append(1)
            if l[i][0] == '-': signs.append(-1)
        return permut, signs

    def createNpArray(self, linesToSkip=1, oldTimeIndex=0):
        try:
            self.npArray = np.loadtxt( StringIO(self.data), delimiter='\t', skiprows=linesToSkip )
            i = oldTimeIndex
            if i > 0:
                #self.nparraylog[:,[i, 0]] = self.nparraylog[:,[0,i]]
                self.npArray[:,i], self.npArray[:,0] = self.npArray[:,0], self.npArray[:,i].copy()
            self.npArray[:,0] *= 0.001 #convert time from us to ms
            #rotations
            if self.logType == cLOGTYPE_NTLOGGER:
            
                imu1Orientation = None
                if self.logOptions.imu1OrientationFlag == 1 and self.auxiliaryData.imu1Orientation != None: 
                    imu1Orientation = self.auxiliaryData.imu1Orientation
                elif self.logOptions.imu1OrientationFlag == 2 and self.logOptions.imu1OrientationEnum != 0: 
                    imu1Orientation = self.logOptions.imu1OrientationEnum - 1
                if imu1Orientation != None and imu1Orientation != 0: #rotate it!    
                    permut, signs = self.getImuPermutSign(imu1Orientation)
                    iax = self.logItemList.getIndexByName('ax1raw')
                    igx = iax + 3
                    iap0, iap1, iap2 = iax+permut[0], iax+permut[1], iax+permut[2]
                    igp0, igp1, igp2 = igx+permut[0], igx+permut[1], igx+permut[2]
                    #my_array[:, 0], my_array[:, 1] = my_array[:, 1], my_array[:, 0].copy()
                    #self.npArray[:,iaz] *= -1
                    #somehow must be on one line!
                    self.npArray[:,iax],self.npArray[:,iax+1],self.npArray[:,iax+2] = self.npArray[:,iap0].copy(),self.npArray[:,iap1].copy(),self.npArray[:,iap2].copy()
                    self.npArray[:,igx],self.npArray[:,igx+1],self.npArray[:,igx+2] = self.npArray[:,igp0].copy(),self.npArray[:,igp1].copy(),self.npArray[:,igp2].copy()
                    for i in range(3):
                        if signs[i] < 0: 
                            self.npArray[:,iax+i] *= -1
                            self.npArray[:,igx+i] *= -1

                imu2Orientation = None
                if self.logOptions.imu2OrientationFlag == 1 and self.auxiliaryData.imu2Orientation != None: 
                    imu2Orientation = self.auxiliaryData.imu2Orientation
                elif self.logOptions.imu2OrientationFlag == 2 and self.logOptions.imu2OrientationEnum != 0: 
                    imu2Orientation = self.logOptions.imu2OrientationEnum - 1
                if imu2Orientation != None and imu2Orientation != 0: #rotate it!    
                    permut, signs = self.getImuPermutSign(imu2Orientation)
                    iax = self.logItemList.getIndexByName('ax2raw')
                    igx = iax + 3
                    iap0, iap1, iap2 = iax+permut[0], iax+permut[1], iax+permut[2]
                    igp0, igp1, igp2 = igx+permut[0], igx+permut[1], igx+permut[2]
                    self.npArray[:,iax],self.npArray[:,iax+1],self.npArray[:,iax+2] = self.npArray[:,iap0].copy(),self.npArray[:,iap1].copy(),self.npArray[:,iap2].copy()
                    self.npArray[:,igx],self.npArray[:,igx+1],self.npArray[:,igx+2] = self.npArray[:,igp0].copy(),self.npArray[:,igp1].copy(),self.npArray[:,igp2].copy()
                    for i in range(3):
                        if signs[i] < 0: 
                            self.npArray[:,iax+i] *= -1
                            self.npArray[:,igx+i] *= -1
            #calculations
            for c in self.logOptions.calculationDict:
                if c['check'].checkState() != QtCore.Qt.Checked: continue
                if c['value'].currentIndex() == 0: continue
                i = self.logItemList.getIndexByName(c['value'].currentText())
                if i == None: continue
                try:
                    scale = eval(c['scale'].text())
                except:
                    if not 'ERR' in c['scale'].text(): c['scale'].setText(c['scale'].text()+'ERR')
                    continue
                try:
                    offset = eval(c['offset'].text())
                except:
                    if not 'ERR' in c['offset'].text(): c['offset'].setText(c['offset'].text()+'ERR')
                    continue
                if scale == 1.0 and offset == 0.0: continue
                #print('calc', c['value'].currentText(), i, scale, offset)
                if scale != 1.0: self.npArray[:,i] *= scale
                if offset != 0.0: self.npArray[:,i] += offset
        except:
            self.npArray = np.zeros((0,0)) #None
            self.logType = cLOGTYPE_UNINITIALIZED

    #this can be called by a caller to transfer data to itself
    def copyToDataContainer(self, dataContainer):
        self.emitProgress(5)
        dataContainer.auxiliaryData = self.auxiliaryData
        if self.logType != cLOGTYPE_NTLOGGER or self.auxiliaryData.imu1Orientation == None:
            dataContainer.wImu1Orientation.setCurrentIndex(0)
        elif self.logOptions.imu1OrientationFlag != 2: #not 'fixed'
            dataContainer.wImu1Orientation.setCurrentIndex( self.auxiliaryData.imu1Orientation + 1 )
        if self.logType != cLOGTYPE_NTLOGGER or self.auxiliaryData.imu2Orientation == None:
            dataContainer.wImu2Orientation.setCurrentIndex(0)
        elif self.logOptions.imu2OrientationFlag != 2: #not 'fixed'
            dataContainer.wImu2Orientation.setCurrentIndex( self.auxiliaryData.imu2Orientation + 1 )
            
        if self.isRecalculate: #only copy over what has been changed
            dataContainer._npArray = self.npArray
            dataContainer._npArrayPtr = self.npArray.shape[0]
            return

        dataContainer.fileName = self.fileName
        dataContainer.wAutopilotSystemTime.setText( self.auxiliaryData.autopilotSystemTime )

        self.emitProgress(10)
        dataContainer.wTrafficText.setPlainText( self.traffic )
#        dataContainer.wTrafficText.setPlainText( '' )
#        dataContainer.wTrafficText.appendHtml( self.traffic )

        self.emitProgress(40)
        dataContainer.wInfoText.setPlainText( self.info )
                
        self.emitProgress(70)
        dataContainer.data = self.data
        dataContainer.gyroflowData = self.gyroflowData

        self.emitProgress(80)
        dataContainer._npArray = self.npArray
        dataContainer._npArrayPtr = self.npArray.shape[0]
        #dataContainer.npPlotView = self.npArray #by default plot view is identical to npArray
        
        self.emitProgress(95)
        dataContainer.logItemList = self.logItemList
        dataContainer.logType = self.logType
        dataContainer.logVersion = self.logVersion
        dataContainer.logSource = cLOGSOURCE_LOAD


class cSaveLogThread(cWorkerThread):

    def __init__(self, _dataContainer):
        super().__init__()
        self.dataContainer = _dataContainer
        self.fileName = ''
        self.saveGraphData = False

    def setFile(self, _fileName):
        self.fileName = _fileName

    def setSaveGraphData(self, _saveGraphData, _saveOnlySelected=False, _saveDecimated=False, _saveDecimatedDecimation=1):
        self.saveGraphData = _saveGraphData
        self.saveOnlySelected = _saveOnlySelected 
        self.saveDecimated = _saveDecimated
        self.saveDecimatedDecimation = _saveDecimatedDecimation
        
    def runCallback(self):
        self.emitProgress(0)
        if self.fileName.lower().endswith('.csv'):
            # with open( fileName, 'w') as F: doesn't catch error when a file is used by some other program!!
            try: F = open( self.fileName, 'w')
            except IOError: pass
            else:
                if self.saveDecimated:
                    print('Save with decimation', self.saveDecimatedDecimation)
                    datalist = self.dataContainer.data.split('\n')
                    count = 0
                    for line in datalist:
                        if count == 0:
                            F.write( line.replace('\t',',') )
                            F.write( '\n' )
                        count += 1
                        if count >= self.saveDecimatedDecimation: count = 0
                else:
                    F.write( self.dataContainer.data.replace('\t',',') )
                F.close()
        elif self.fileName.lower().endswith('.gcsv'):
            try: F = open( self.fileName, 'w')
            except IOError: pass
            else:
                F.write( 'GYROFLOW IMU LOG\n' )
                F.write( 'version,1.1\n' )
                i1 = self.dataContainer.auxiliaryData.imu1Orientation
                if i1 != None and i1 >= 0 and i1 <= 23:
                    # TODO: the gf values are totally arbitrary momentarily, and surely not correct !!
                    # I just made them to reflect the STorM32 notation, so one can work out by time
                    storm32togyrofloworient = [
                        'XYZ', # no.0 x y z
                        'yXZ', # no.1 -y x z
                        'xyZ', # no.2 -x -y z
                        'YxZ', # no.3 y -x z
                        'YZX', # no.4 y z x
                        'zYX', # no.5 -z y x
                        'yzX', # no.6 -y -z x
                        'ZyX', # no.7 z -y x
                        'ZXY', # no.8 z x y
                        'xZY', # no.9 -x z y
                        'zxY', # no.10 -z -x y
                        'XzY', # no.11 x -z y
                        'YXz', # no.12 y x -z
                        'xYz', # no.13 -x y -z
                        'yxz', # no.14 -y -x -z
                        'Xyz', # no.15 x -y -z
                        'ZYx', # no.16 z y -x
                        'yZx', # no.17 -y z -x
                        'zyx', # no.18 -z -y -x
                        'Yzx', # no.19 y -z -x
                        'XZy', # no.20 x z -y
                        'zXy', # no.21 -z x -y
                        'xzy', # no.22 -x -z -y
                        'Zxy', # no.23 z -x -y
                        ]
                    F.write( 'orientation,' + storm32togyrofloworient[i1] +'\n' )
                F.write( 'tscale,0.0015\n' )
                F.write( 'gscale,0.001065264436\n' ) #+/-2000 deg/s -> (2000 * pi/180)/2^15 = 0.001065264436
                F.write( 'ascale,0.0001220703125\n' ) # +/-4 g -> 4/2^15 = 0.0001220703125
                F.write( 't,gx,gy,gz,ax,ay,az\n' )
                F.write( self.dataContainer.gyroflowData )
                F.close()
               
            ''' is kept as example here
        elif self.fileName.lower().endswith('.cfl'):
            if len(self.dataContainer.rawData)<=0: return #no raw data available
            try: F = open( self.fileName, 'wb')
            except IOError: pass
            else:
                logItemList = cLogItemList()
                CFBlackbox = cCFBlackbox(logItemList)
                fv = self.dataContainer.getSTorM32FirmwareVersion()
                lv = self.dataContainer.logVersion
                F.write( CFBlackbox.header(fv,lv) )
                lastState = -1
                index = 0
                self.startProgress(5, len(self.dataContainer.rawData))
                for data in self.dataContainer.rawData:
                    if( lastState!=6 and data[8]==6 ):
                        F.write( CFBlackbox.dataEBeep( data[0]) )
                    if( lastState>0 and data[8]==0 ):
                        F.write( CFBlackbox.footer() )
                        F.write( CFBlackbox.header() )
                    lastState = data[8]
                    F.write( CFBlackbox.dataIFrame(index, data) )
                    index += 1
                    self.updateProgress()
                F.write( CFBlackbox.footer() )
                F.close()
            '''
        else:
            #print("SAVE IT AS WHATEVER")
            try: F = open( self.fileName, 'w')
            except IOError: pass
            else:
                if self.saveDecimated:
                    print('Save with decimation', self.saveDecimatedDecimation)
                    datalist = self.dataContainer.data.split('\n')
                    count = 0
                    for line in datalist:
                        if count == 0:
                            F.write( line )
                            F.write( '\n' )
                        count += 1
                        if count >= self.saveDecimatedDecimation: count = 0
                else:           
                    F.write( self.dataContainer.data )
                F.close()
        self.emitProgress(100)

        

###################################################################
# MAIN
###################################################################
# cMain
# that's the real beef
#-----------------------------------------------------------------------------#
class cMain(QMainWindow,wMainWindow):

    appPalette = 'Fusion'
    
    def __init__(self, _winScale, _appPalette, _arg):
        super().__init__()

        if( whichUiToUse=='ow_py' ):
            self.setupUi(self, _winScale)
        else:
            self.setupUi(self)
        appPalette = _appPalette #this is needed to allow writing into ini file
        self.setAcceptDrops(True)

        self.actionLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.actionSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.actionClear.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))

        self.bLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.bSave.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.bCancelLoad.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))

        self.fileDialogDir = ''

        self.bPlaybackBegin.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.bPlaybackSkipBackward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.bPlaybackPlayStop.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.bPlaybackSkipForward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.bPlaybackEnd.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.wPlaybackSpeedFactor.addItems( ['8 x','4 x','2 x','1 x','1/2 x','1/4 x','1/8 x'] )
        self.wPlaybackSpeedFactor.setCurrentIndex( 3 )
        self.wGraphZoomFactor.addItems( ['100 %','10 %','1 %','30 s','10 s','5 s','2 s','1 s','250 ms','100 ms'] )
        self.wGraphZoomFactor.setCurrentIndex( 4 )

        self.bPlaybackBegin.hide()
        self.bPlaybackSkipBackward.hide()
        self.bPlaybackPlayStop.hide()
        self.bPlaybackSkipForward.hide()
        self.bPlaybackEnd.hide()
        self.wPlaybackSpeedFactor.hide()
        self.wPlaybackSpeedFactorLabel.hide()

        #don't know how to do this with layouts/QtDesigner, so add brute-force by hand
        self.wAutopilotSystemTime = QtWidgets.QLabel(self.wTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wAutopilotSystemTime.sizePolicy().hasHeightForWidth())
        self.wAutopilotSystemTime.setSizePolicy(sizePolicy)
        self.wAutopilotSystemTime.setMinimumWidth(int(_winScale*300)) #100 was too short, 200 seems plenty
        self.wAutopilotSystemTime.setText("")
        self.wAutopilotSystemTime.setObjectName("wAutopilotSystemTime")
        self.wAutopilotSystemTime.move(int(_winScale*225),int(_winScale*4)) #170, position of Graph is 1??,4

        #this holds all data and related info
        self.dataContainer = cLogDataContainer(self.wTrafficText, self.wInfoText, 
            self.wAutopilotSystemTime, self.wImu1Orientation, self.wImu2Orientation, self.wGraphFftLength)

        #threads for file load and save operations
        self.loadLogThread = cLoadLogThread()
        self.loadLogThread.finished.connect(self.loadLogFileDone)
        self.loadLogThread.progress.connect(self.loadLogFileProgress)

        self.saveLogThread = cSaveLogThread(self.dataContainer)
        self.saveLogThread.finished.connect(self.saveLogFileDone)
        self.saveLogThread.progress.connect(self.saveLogFileProgress)

        #holds the list of names of the items in the data log
        #holds the list of categories and items, as needed for the selctor tree
        self.logItemNameList = []
        self.graphSelectorList = []
        self.setGraphSelectorTreeFromLogItemList(self.dataContainer.logItemList)
        self.currentGraphIndexes = None #to avoid that indexes needs to be build at each updateGraph()
        self.setCurrentIndexes()

        imuOrientation = cNTImuOrientation()
        self.wImu1OrientationFlag.addItems( imuOrientation.orientationFlagList )
        self.wImu1OrientationFlag.setCurrentIndex( 1 )
        self.wImu2OrientationFlag.addItems( imuOrientation.orientationFlagList )
        self.wImu2OrientationFlag.setCurrentIndex( 1 )
        self.wImu1Orientation.addItems( imuOrientation.orientationList )
        self.wImu1Orientation.setCurrentIndex( 0 )
        self.wImu2Orientation.addItems( imuOrientation.orientationList )
        self.wImu2Orientation.setCurrentIndex( 0 )

        self.calculationDict = []
        self.calculationDict.append({'check':self.wCalc1Check, 'value':self.wCalc1Value, 'scale':self.wCalc1Scale, 'offset':self.wCalc1Offset})
        self.calculationDict.append({'check':self.wCalc2Check, 'value':self.wCalc2Value, 'scale':self.wCalc2Scale, 'offset':self.wCalc2Offset})
        self.calculationDict.append({'check':self.wCalc3Check, 'value':self.wCalc3Value, 'scale':self.wCalc3Scale, 'offset':self.wCalc3Offset})
        self.calculationDict.append({'check':self.wCalc4Check, 'value':self.wCalc4Value, 'scale':self.wCalc4Scale, 'offset':self.wCalc4Offset})
        self.calculationDict.append({'check':self.wCalc5Check, 'value':self.wCalc5Value, 'scale':self.wCalc5Scale, 'offset':self.wCalc5Offset})
        self.calculationDict.append({'check':self.wCalc6Check, 'value':self.wCalc6Value, 'scale':self.wCalc6Scale, 'offset':self.wCalc6Offset})
        #this is initialized with default, we only allow default, we also replace Time by '-'
        calculationItems = ['-'] + self.logItemNameList[1:]
        for c in self.calculationDict:
            c['value'].addItems(calculationItems)
        self.clearCalculations()

        #add two plot window frames, to host the various plots
        #self.pqGraphicsWindow = pg.GraphicsWindow()
        self.pqGraphicsWindow = pg.GraphicsLayoutWidget() #this is needed instead of selfpqPlotWidget = pg.PlotWidget() for the mouse/vb to work
        self.pqGraphicsWindow.ci.setContentsMargins(3,3,9,3)
        self.pqGraphicsWindow.ci.setSpacing(0)
        #self.pqGraphicsWindow.setBackground(None)
        self.wGraphPlotAreaLayout.addWidget(self.pqGraphicsWindow)
        self.pqGraphicsWindowBottom = self.pqGraphicsWindow.addLayout(row=1, col=0)
        self.pqGraphicsWindowBottom.setContentsMargins(0,0,0,0)

        #add the main data plot window
        self.pqPlotWidget = self.pqGraphicsWindow.addPlot(row=0, col=0)
        self.pqPlotWidget.setLabel('bottom', 'Time', units='s')
        self.pqPlotWidget.showGrid(x=True, y=True, alpha=0.33)
        self.pqPlotWidget.setYRange( 0.0, 1.0 )
        self.pqPlotWidget.setXRange( 0.0, 1.0 )
        self.pgGraphTimeLine = pg.InfiniteLine(angle=90, movable=False)
        colstr = pg.colorStr( pg.mkColor(pg.getConfigOption('foreground')) )[:6]
        self.wGraphCursorFormatStr = "<span style='color: #"+colstr+"'>x = %0.4f, y = %0.4f</span>"
        self.wGraphTimeFormatStr = "<span style='color: #"+colstr+"'>%s</span>"

        #add FFT plot window
        self.pqFftWidget = self.pqGraphicsWindowBottom.addPlot(row=0,col=0)
        self.pqFftWidget.setLabel('bottom', 'Frequency', units='Hz')
        self.pqFftWidget.showGrid(x=True, y=True, alpha=0.33)
        self.pqFftWidget.setYRange( 0.0, 1.0 )
        self.pqFftWidget.setXRange( 0.0, 333.0 )
        self.wGraphFftLength.addItems( ['2048/3.1s','1024/1.5s','512/0.77s','256/0.38s'] )
        self.wGraphFftLength.setCurrentIndex( 1 )
        self.wGraphFftWindow.addItems( ['square','bartlett','blackman','hamming','hanning','kaiser2','kaiser3'] )
        self.wGraphFftWindow.setCurrentIndex( 3 )
        self.wGraphFftOutput.addItems( ['amplitude','psd (lin f)','psd (log f)'] )
        self.wGraphFftOutput.setCurrentIndex( 0 )
        self.wGraphFftPreFilter.addItems( ['none','average','1 Hz','2 Hz','4 Hz','8 Hz'] )
        self.wGraphFftPreFilter.setCurrentIndex( 1 )
        self.wFftCursorFormatStr = "<span style='color: #"+colstr+"'>f = %0.1f Hz, y = %0.4f</span>"
        self.wFftCursor.setText( self.wFftCursorFormatStr % (0,0))
        self.wFftZoomFactor.addItems( ['full','1/2','1/3','1/4','1/5'] )
        self.wFftZoomFactor.setCurrentIndex( 0 )

        #self.wGraphComment.setText('')
        self.wGraphComment.hide()

        #add com port widget, and associated serial
        self.wRecordComPort = cSerialPortComboBox(self.centralwidget, _winScale)
        self.topLayout.addWidget(self.wRecordComPort)
        self.serialStream = cSerialStream()
        self.serialReaderThread = cNTSerialReaderThread(self.serialStream) #SSS
        
        self.serialReaderThread.finished.connect(self.serialReaderThreadDone)
        self.serialReaderThread.newSerialDataAvailable.connect(self.serialReaderThreadNewDataAvailable)

        self.pqGraphicsWindow.scene().sigMouseMoved.connect(self.updateGraphCursorEvent)
        self.pqPlotWidget.sigXRangeChanged.connect(self.updateGraphRangeChangedEvent)
        self.wGraphTimeSlider.valueChanged.connect(self.updateGraphTimeSliderValueChangedEvent)

        self.bScreenShot.clicked.connect(self.doScreenShot)
        self.bAutoRangeAll.clicked.connect(self.doAutoRangeAll)
        self.bXAutoRange.clicked.connect(self.doXAutoRange)
        self.bYAutoRangeFull.clicked.connect(self.doYAutoRangeFull)
        self.bYAutoRangeView.clicked.connect(self.doYAutoRangeView)

        self.bGraphSelectorClear.clicked.connect(self.clearGraphSelection)
        self.wGraphSelectorTree.itemChanged.connect(self.updateGraphOnItemChanged)
        self.bGraphShowFft.clicked.connect(self.showFftClicked)
        self.bGraphShowRecord.clicked.connect(self.showRecordClicked)
        self.bGraphShowPoints.clicked.connect(self.updateGraphOnItemChangedNoAutoRange)

        #self.wGraphFftLength.currentIndexChanged.connect(self.updateGraphOnFftParameterChanged)
        self.wGraphFftLength.activated.connect(self.updateGraphOnFftParameterChanged)
        self.wGraphFftWindow.activated.connect(self.updateGraphOnFftParameterChanged)
        self.wGraphFftOutput.activated.connect(self.updateGraphOnFftParameterChanged)
        self.wGraphFftPreFilter.activated.connect(self.updateGraphOnFftParameterChanged)
        self.wFftZoomFactor.currentIndexChanged.connect(self.updateGraphOnFftZoomFactorChanged)

        self.bRecordStartStop.clicked.connect(self.doRecordStartStopClicked)
        self.bRecordClear.clicked.connect(self.doRecordClearClicked)

        self.readSettings()

        self.wProgressBar.hide()
        self.bCancelLoad.hide()
        self.pqFftWidget.hide()
        self.wFftCursor.hide()
        self.wGraphBottomArea.hide()
        self.wGraphFftLength.hide()
        self.wGraphFftWindow.hide()
        self.wGraphFftOutput.hide()
        self.wGraphFftPreFilter.hide()
        self.bRecordStartStop.hide()
        self.bRecordClear.hide()
        self.wRecordComPort.hide()

        self.setGraphControlWidgetsToDefault()
        
        self.clearPlot()
        self.updateGraphTime()
        
        #idea is from here: https://stackoverflow.com/questions/6215690/how-to-execute-a-method-automatically-after-entering-qt-event-loop
        # it's a bit stupid though, is there a means to detect if the event loop is running? when a multishot timer could be used
        if _arg:
            self._arg = _arg
            QtCore.QTimer.singleShot(500, self.doSingleShot) 
        
    def doSingleShot(self):
        self.doLoadLogFile(self._arg)

    def setGraphSelectorTreeFromLogItemList(self,_logItemList):
        ##self.wGraphSelectorTree.itemChanged.disconnect(self.updateGraphOnItemChanged)
        # it's crucial to avoid that each changed sub level item is called
        self.wGraphSelectorTree.blockSignals(True)
        # clear stuff
        self.wGraphSelectorTree.clear()
        # populate stuff
        self.logItemNameList = _logItemList.getNamesAsList()
        self.graphSelectorList = _logItemList.getGraphSelectorList()
        for entry in self.graphSelectorList:
            item = QTreeWidgetItem(self.wGraphSelectorTree) #also does addTopLevelItem(item)
            item.setText(0, entry[0])
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked) #this is required, since otherwise the item might happen to have no checkbox!
            if len(entry[1])>1:
              for index in entry[1]:
                child = QTreeWidgetItem(item)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, self.logItemNameList[index])
                child.setCheckState(0, Qt.Unchecked)
        i = _logItemList.getGraphSelectorDefaultIndex(self.graphSelectorList) 
        if i:
            self.wGraphSelectorTree.topLevelItem(i).setCheckState(0, QtCore.Qt.Checked)
            self.wGraphSelectorTree.blockSignals(False)
            return
        if len(self.graphSelectorList):
            self.wGraphSelectorTree.topLevelItem(0).setCheckState(0, QtCore.Qt.Checked)
        self.wGraphSelectorTree.blockSignals(False)
        ##self.wGraphSelectorTree.itemChanged.connect(self.updateGraphOnItemChanged)

    #slot for signal clicked from bGraphSelectorClear
    def clearGraphSelection(self,):
        self.wGraphSelectorTree.blockSignals(True)
        for i in range(self.wGraphSelectorTree.topLevelItemCount()):
            self.wGraphSelectorTree.topLevelItem(i).setCheckState(0, QtCore.Qt.Unchecked)
        self.wGraphSelectorTree.blockSignals(False)
        self.setCurrentIndexes()
        self.updateGraph()

    #slot for signal ClearCalc, connection to signals in QTDesigner
    def clearCalculations(self):
        for c in self.calculationDict:
            c['check'].setCheckState(QtCore.Qt.Unchecked)
            c['value'].setCurrentIndex(0)
            c['scale'].setText(str(1))
            c['offset'].setText(str(0))


    #slot for signal ClearLog File, connection to signals in QTDesigner
    def clearLogFile(self):
        self.setLogSourceToUninitialized(True) #unche all, incl. rec

    #slot for signal progress of cLoadLogThread
    # is called by WorkerThread to update progress bar
    def loadLogFileProgress(self):
        self.wProgressBar.setValue(self.loadLogThread.progressValue)

    #slot for signal progress of cSaveLogThread
    # is called by WorkerThread to update progress bar
    def saveLogFileProgress(self):
        self.wProgressBar.setValue(self.saveLogThread.progressValue)

    def workerThreadPrepare(self, _message):
        self.bLoad.setEnabled(False)
        self.actionLoad.setEnabled(False)
        self.bSave.setEnabled(False)
        self.bReload.setEnabled(False)
        self.bRecalculate.setEnabled(False)
        self.bClearCalculations.setEnabled(False)
        self.wLoadOptionsGroupBox.setEnabled(False)
        self.wCalculateOptionsGroupBox.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.actionSaveGraphData.setEnabled(False)
        self.actionClear.setEnabled(False)
        self.bRecordClear.setEnabled(False)
        self.bCancelLoad.show()
        self.wProgressBar.show()
        self.wLogFileName.setText(_message)

    def workerThreadFinish(self):
        self.bLoad.setEnabled(True)
        self.actionLoad.setEnabled(True)
        if self.dataContainer.logType != cLOGTYPE_UNINITIALIZED:
            self.bSave.setEnabled(True)
            self.bReload.setEnabled(True)
            self.bRecalculate.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionSaveGraphData.setEnabled(True)
            self.actionClear.setEnabled(True)
            self.bRecordClear.setEnabled(True)
        self.bClearCalculations.setEnabled(True)
        self.wLoadOptionsGroupBox.setEnabled(True)
        self.wCalculateOptionsGroupBox.setEnabled(True)
        self.bCancelLoad.hide()
        self.wProgressBar.hide()
        self.wLogFileName.setText(self.dataContainer.fileName)

    def loadLogFileIsAllowed(self):
        if self.loadLogThread.isRunning(): return False
        if self.bLoad.isEnabled() and self.actionLoad.isEnabled(): return True
        return False

    def getLogOptionsForLoadOrRecalculate(self):
        logOptions = cNTLogOptions()
        if( self.bLoadTraffic.checkState() == QtCore.Qt.Checked ): logOptions.setCreateFullTraffic(True)
        if( self.bSortParameterList.checkState() == QtCore.Qt.Checked ): logOptions.setSortParameters(True)
        #sanitize imu orientation rotation
        if self.wImu1OrientationFlag.currentIndex() != 2: #not 'fixed', 'off' or 'auto'
            self.wImu1Orientation.setCurrentIndex(0) #set to unknown
        if self.wImu2OrientationFlag.currentIndex() != 2:  #not 'fixed', 'off' or 'auto'
            self.wImu2Orientation.setCurrentIndex(0) #set to unknown
        logOptions.setImu1( self.wImu1OrientationFlag.currentIndex(), self.wImu1Orientation.currentIndex() ) 
        logOptions.setImu2( self.wImu2OrientationFlag.currentIndex(), self.wImu2Orientation.currentIndex() ) 
        logOptions.setCalculationDict(self.calculationDict)
        return logOptions

    def doLoadLogFile(self,fileName):
        if self.loadLogThread.isRunning(): return
        self.workerThreadPrepare( "Loading... "+fileName )
        logOptions = self.getLogOptionsForLoadOrRecalculate()
        self.loadLogThread.setLoadFile(fileName, logOptions)
        self.loadLogThread.start()

    def doRecalculateLogFile(self):
        if self.loadLogThread.isRunning(): return
        self.workerThreadPrepare( "Recalculating... "+self.dataContainer.fileName )
        logOptions = self.getLogOptionsForLoadOrRecalculate()
        self.loadLogThread.setRecalculate(self.dataContainer, logOptions)
        self.loadLogThread.start()

    #slot for signal cancel of cLoadLogThread
    # is called then Cancel button is hit
    def loadLogFileCancel(self):
        self.loadLogThread.cancel() #simply cancel all
        self.saveLogThread.cancel()
        self.workerThreadFinish()

    #slot for signal Load Log File, connection to signals in QTDesigner
    # is called then Load button or Load action is hit
    def loadLogFile(self):
        if self.loadLogThread.isRunning():
            return
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            'Load Data Logger file',
            self.fileDialogDir,
            '*.ntlog *.log *.dat *.txt *.csv;;*.ntlog;;*.log;;*.dat;;*.txt;;*.csv;;All Files (*)'
            )
        if fileName:
            self.doLoadLogFile(fileName)

    def reloadLogFile(self):
        if self.loadLogThread.isRunning():
            return
        fileName = self.dataContainer.fileName
        if fileName:
            self.doLoadLogFile(fileName)
            
    def recalculateLogFile(self):
        if self.loadLogThread.isRunning():
            return
        self.doRecalculateLogFile()

    #slot for signal finished of cLoadLogThread
    # is called when WorkerThread finishes
    def loadLogFileDone(self):
        if( self.loadLogThread.canceled ): return
        self.loadLogThread.copyToDataContainer(self.dataContainer) #copy loaded results to your dataContainer
        self.dataContainer.setLogType() #determine some metrics for the data, such as e.g. dT
        self.workerThreadFinish()
        # do the final touches
        if not self.loadLogThread.isRecalculate:
            self.setLogSourceToLoad() #doesn't do anything if it was already cLOGSOURCE_RECORD before
            self.setGraphSelectorTreeFromLogItemList(self.dataContainer.logItemList)
            self.bGraphShowPoints.setCheckState(QtCore.Qt.Unchecked)
        self.setCurrentIndexes()
        self.updateGraph()

    #slot for signal Save Into File, connection to signals in QTDesigner
    # is called then Save button or Save action is hit
    def saveDataIntoFile(self):
        if self.saveLogThread.isRunning():
            return
        ext = '*.dat;;*.txt;;*.csv;;*.gcsv'
        ext += ';;All Files (*)'
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            'Save Data to file',
            self.fileDialogDir,
            ext #'*.dat;;*.txt;;*.csv;;PX4 (*.bin);;CF-Blackbox (*.cfl)'
            )
        if fileName:
            self.workerThreadPrepare( 'saving... ' )
            self.saveLogThread.setFile(fileName)
            self.saveLogThread.setSaveGraphData(False)
            self.saveLogThread.start()

    #slot for signal Save Graph Data Into File, connection to signals in QTDesigner
    # is called then Save Graph Data action is hit
    def saveGraphDataIntoFile(self):
        print('SaveGraphData')
        if self.saveLogThread.isRunning():
            return
        ext = '*.dat;;*.txt;;*.csv'
        ext += ';;All Files (*)'
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            'Save Graph Data to file',
            self.fileDialogDir,
            ext #'*.dat;;*.txt;;*.csv;;PX4 (*.bin);;CF-Blackbox (*.cfl)'
            )
        if fileName:
            self.workerThreadPrepare( 'saving... ' )
            self.saveLogThread.setFile(fileName)
            self.saveLogThread.setSaveGraphData(
                True,
                self.bSaveOnlySelected.checkState() == QtCore.Qt.Checked,
                self.bSaveDecimated.checkState() == QtCore.Qt.Checked,
                int(self.bSaveDecimatedDecimation.text())
                )
            self.saveLogThread.start()

    #slot for signal finished of cSaveLogThread
    # is called when WorkerThread finishes
    def saveLogFileDone(self):
        if( self.saveLogThread.canceled ): return
        self.workerThreadFinish()
        
        
    #slot for signal ScreenShot
    def doScreenShot(self):
        #if not self.dataContainer.hasData():
        #    return
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            'Save Screenshot to file',
            self.fileDialogDir,
            '*.jpg'
            )
        if fileName:
            #self.wGraphComment.setText(self.dataContainer.fileName)
            #self.wGraphComment.show()
            #filename = 'C:/Users/Olli/Desktop/screenshot.jpg'
            p = self.wGraphAreaWidget.grab()
            if not fileName.lower().endswith('.jpg'): fileName += '.jpg'
            p.save(fileName, 'jpg')
            #self.wGraphComment.hide()


    def clearData(self):
        self.dataContainer.clear()
        self.wLogFileName.setText(self.dataContainer.fileName)
        self.setGraphSelectorTreeFromLogItemList(self.dataContainer.logItemList)
        self.setCurrentIndexes()

    def clearPlot(self):
        self.updateGraphLegend()
        self.updateGraphCursor()
        self.updateGraphTimeLabel()
        self.updateGraphMaxTimeLabel()
        #self.updateGraphTime()
        self.pqPlotWidget.clear() #?? does this do the other 3 updates? no
        self.pqFftWidget.clear()

    def setFileWidgetsToDefault(self):
        self.bLoad.setEnabled(True)
        self.actionLoad.setEnabled(True)
        # this must be done where the button is shown!
        if self.dataContainer.logType != cLOGTYPE_UNINITIALIZED:
            self.bSave.setEnabled(True)
            self.bReload.setEnabled(True)
            self.bRecalculate.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionSaveGraphData.setEnabled(True)
            self.actionClear.setEnabled(True)
            # this must be done where the button is shown!
            self.bRecordStartStop.setEnabled(False)
            self.bRecordClear.setEnabled(True)  #can be done since it doesn't hurt, but helps when button visible
        else:
            self.bSave.setEnabled(False)
            self.bReload.setEnabled(False)
            self.bRecalculate.setEnabled(False)
            self.actionSave.setEnabled(False)
            self.actionSaveGraphData.setEnabled(False)
            self.actionClear.setEnabled(False)
            # this must be done where the button is shown!
            self.bRecordStartStop.setEnabled(True)
            self.bRecordClear.setEnabled(False) #can be done since it doesn't hurt, but helps when button visible
        self.bCancelLoad.hide()
        self.wProgressBar.hide()

    #the following handles the logsource handling
    def setLogSourceToUninitialized(self,uncheckRec=True):
        self.clearData()
        self.clearPlot()
        self.serialReaderThread.clear()
        if uncheckRec:
            self.uncheckShowFftRecord()
        self.setFileWidgetsToDefault()

    def setLogSourceToLoad(self):
        if self.dataContainer.logSource == cLOGSOURCE_RECORD: print('SHIT (1)!!!!') #this should not happen!!!
        self.setFileWidgetsToDefault()
        if self.dataContainer.logSource == cLOGSOURCE_LOAD: return
        #it has now been verifyed that log source is cLOGSOURCE_UNINITIALIZED
        # switch to cLOGSOURCE_LOAD
#XX        self.bLoad.setEnabled(True)
#XX        self.actionLoad.setEnabled(True)  #we require an explicit clear before we allow to load
        #this must be done where the button is shown:
        # self.bRecordStartStop.setEnabled(False)
        # self.bRecordStartStop.setText('Rec Start')
        self.dataContainer.logSource = cLOGSOURCE_LOAD

    def setLogSourceToRecord(self):
        if self.dataContainer.logSource == cLOGSOURCE_LOAD: print('SHIT (2)!!!!') #this should not happen!!!
        if self.dataContainer.logSource == cLOGSOURCE_RECORD: return
        #it has now been verifyed that log source is cLOGSOURCE_UNINITIALIZED
        # switch to cLOGSOURCE_RECORD
        self.bLoad.setEnabled(False)
        self.actionLoad.setEnabled(False)  #we require an explicit clear before we allow to load
        #this must be done where the button is shown
        # self.bRecordStartStop.setEnabled(True)
        # self.bRecordStartStop.setText('Rec Start')
        self.dataContainer.logSource = cLOGSOURCE_RECORD


    #the following handles the fft, bode plot, and rec checkboxes in a radiobutton type way
    def hideFft(self,):
        self.pqGraphicsWindow.ci.setSpacing(0)
        self.pqFftWidget.hide()
        self.wFftCursor.hide()
        self.wGraphBottomArea.hide()
        self.wGraphFftLength.hide()
        self.wGraphFftWindow.hide()
        self.wGraphFftOutput.hide()
        self.wGraphFftPreFilter.hide()

    def showFft(self,):
        self.pqGraphicsWindow.ci.setSpacing(3)
        self.pqFftWidget.show()
        self.wFftCursor.show()
        self.wGraphBottomArea.show()
        self.wGraphFftLength.show()
        self.wGraphFftWindow.show()
        self.wGraphFftOutput.show()
        self.wGraphFftPreFilter.show()

    def hideRecord(self,):
        self.bRecordStartStop.hide()
        self.bRecordClear.hide()
        self.wRecordComPort.hide()

    def hideFftRecord(self,):
        self.hideFft()
        self.hideRecord()

    def uncheckShowFft(self,):
        self.bGraphShowFft.setCheckState(QtCore.Qt.Unchecked)
        self.hideFft()

    def uncheckShowRecord(self,):
        self.bGraphShowRecord.setCheckState(QtCore.Qt.Unchecked)
        self.hideRecord()

    def uncheckShowFftRecord(self,):
        self.uncheckShowFft()
        self.uncheckShowRecord()

    def showFftClicked(self,):
        self.serialReaderThread.cancelIfRunning()
        if( self.bGraphShowFft.checkState()==QtCore.Qt.Checked ):
            self.showFft()
            self.updateFftGraph(True) #False) #for some reason True doesn't work properly ????
        else:
            self.hideFft()

    def showRecordClicked(self,):
        if( self.bGraphShowRecord.checkState()==QtCore.Qt.Checked ):
            self.bRecordStartStop.show()
            self.bRecordClear.show()
            self.wRecordComPort.show()
            #this must be done here, where the buttons are shown:
            if( self.dataContainer.logSource == cLOGSOURCE_UNINITIALIZED or
                self.dataContainer.logSource == cLOGSOURCE_RECORD ):
                self.bRecordStartStop.setEnabled(True)
            else:
                self.bRecordStartStop.setEnabled(False)
            if self.dataContainer.logType != cLOGSOURCE_UNINITIALIZED:
                self.bRecordClear.setEnabled(True)
            else:
                self.bRecordClear.setEnabled(False)
        else:
            self.serialReaderThread.cancelIfRunning()
            self.hideRecord()


    #slot for signal itemChanged from wGraphSelectorTree
    # is called when an Item in the GraphSelector is clicked/unclicked
    # it's crucial to avoid this beeing called for every sub level item
    # this exploits the fact that even then a sub level item is clicked the top level item is changed
    def updateGraphOnItemChanged(self,item):
        if item.parent()==None:
            self.setCurrentIndexes()
            self.updateGraph(False)

    #slot for signal clicked from bGraphShowPoints
    def updateGraphOnItemChangedNoAutoRange(self):
        self.setCurrentIndexes()
        self.updateGraph(None)

    #slot for signal currentIndexChanged from bGraphFftLength
    def updateGraphOnFftParameterChanged(self):
        self.setCurrentIndexes()
        self.updateFftGraph(True)

    #slot for signal currentIndexChanged from bFftZoomFactor
    def updateGraphOnFftZoomFactorChanged(self):
        self.setCurrentIndexes()
        self.updateFftGraph(True)

    #Info:
    # self.pqPlotWidget.autoRange() is equal to
    #   bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None) #is QRectF
    #   if bounds is not None: self.pqPlotWidget.setRange(bounds, padding=None)

    #slot for signal doAutoRangeAll from bAutoRangeAll
    def doAutoRangeAll(self):
        bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None)
        if bounds is not None:
            self.pqPlotWidget.setXRange(bounds.left(), bounds.right())
            self.pqPlotWidget.setYRange(bounds.bottom(), bounds.top())
            #self.pqPlotWidget.autoRange()

    #slot for signal doXAutoRange from bXAutoRange
    def doXAutoRange(self):
        bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None)
        if bounds is not None:
            self.pqPlotWidget.setXRange(bounds.left(), bounds.right())

    #slot for signal doYAutoRangeFull from bYAutoRangeFull
    def doYAutoRangeFull(self):
        bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None)
        if bounds is not None:
            self.pqPlotWidget.setYRange(bounds.bottom(), bounds.top())

    #slot for signal doYAutoRangeView from bYAutoRangeView
    def doYAutoRangeView(self):
        #vb.childrenBoundingRect(items=None): (xmin, ymin, dx, dy) of data set
        #viewRange(): [[xmin,xmax],[ymin,ymax]] of plot area
        #viewRect(): (xmin,ymin,dx,dy) of plot area, same as viewRange just as QRectF
        if not self.dataContainer.hasData(): return
        indexes = self.currentGraphIndexes
        if len(indexes) == 0: return
        nr = len(indexes)
        npPlotView = self.dataContainer.getNpPlotView(nr)
        x = npPlotView[:,0] #this is a view, i.e. not a duplicate
        # find indices of visible x axis
        xRange = self.pqPlotWidget.viewRange()[0]
        xminIndex = np.searchsorted(x, xRange[0]) - 1
        xmaxIndex = np.searchsorted(x, xRange[1])
        if xminIndex < 0: xminIndex = 0
        if xmaxIndex > x.size: xmaxIndex = x.size
        # determine y range # ymin = np.amin( np.amin(pv, axis=0)[1:] ) would find minimum in all y axes
        pv = npPlotView[xminIndex:xmaxIndex,:]
        ymin = 1.0e300; ymax = -1.0e300
        for i in range(nr):
            p = pv[:,indexes[i]]
            y = np.amin(p)
            if y < ymin: ymin = y
            y = np.amax(p)
            if y > ymax: ymax = y
        self.pqPlotWidget.setYRange(ymin, ymax)

    def getIndexes(self):
        indexes = []
        for n in range(self.wGraphSelectorTree.topLevelItemCount()):
            item = self.wGraphSelectorTree.topLevelItem(n)
            if item.checkState(0) == QtCore.Qt.Checked:
                indexes += self.graphSelectorList[n][1]
            elif item.checkState(0) != QtCore.Qt.Unchecked:
                for i in range(item.childCount()):
                    if item.child(i).checkState(0) == QtCore.Qt.Checked:
                        indexes += [self.graphSelectorList[n][1][i]]
        return indexes

    def setCurrentIndexes(self):
        self.currentGraphIndexes = self.getIndexes()

    def updateGraph(self, doXYAutorange=True): #True: in xy, False: only in y, None: none
        if not self.dataContainer.hasData(): return
        # get data colums to plot   // with( pg.BusyCursor() ):
        indexes = self.currentGraphIndexes
        # clear
        self.pqPlotWidget.clear()
        self.pqPlotWidget.addItem(self.pgGraphTimeLine, ignoreBounds=True)
        #self.pqPlotWidget.setClipToView(True) #not good
        #self.pqPlotWidget.setDownsampling(auto=True) hmhmhmh
        # add selected plots
        nr = len(indexes)
        npPlotView = self.dataContainer.getNpPlotView(nr)
        x = npPlotView[:,0] #this is a view, i.e. not a duplicate
        if self.bGraphShowPoints.checkState() == QtCore.Qt.Checked:
            for i in range(nr):
                self.pqPlotWidget.plot(x, npPlotView[:,indexes[i]],
                                       pen=(i,nr),
                                       symbol='o', symbolSize=4, symbolBrush=(i,nr), symbolPen=(i,nr) )
        else:
            for i in range(nr):
                self.pqPlotWidget.plot(x, npPlotView[:,indexes[i]], pen=(i,nr) )  ## setting pen=(i,3) automaticaly creates three different-colored pens
        # create label
        self.updateGraphLegend(indexes)
        self.updateGraphMaxTimeLabel(x[-1])
        # handle the time slider
        sliderRange = x[-1]/self.dataContainer.dT() #0.0015
        self.wGraphTimeSlider.setRange( 0, int(sliderRange) )
        self.wGraphTimeSlider.setSingleStep( 10 )
        self.wGraphTimeSlider.setPageStep( int(sliderRange/100.0) )
        # auto range as needed
        if doXYAutorange == None:
            pass
        elif doXYAutorange:
            if self.bYAutoRangeOff.checkState() == QtCore.Qt.Checked: #autorange only in x
                self.pqPlotWidget.disableAutoRange()
                self.doXAutoRange()
            else:
                self.pqPlotWidget.autoRange()
        elif self.bYAutoRangeOff.checkState() != QtCore.Qt.Checked:
            self.doYAutoRangeFull()
        else:
            self.pqPlotWidget.disableAutoRange()
        # handle FFT window
        self.updateFftGraph(True)

    def calculateFftAmplitude(self,signal,signalLen,winType,win,startPos,endPos):
            if winType:
                fft = np.fft.rfft( win*signal, n=signalLen )
            else:
                fft = np.fft.rfft( signal, n=signalLen )
            fftAmplitude = np.abs(fft)/(signalLen/2)
            return fftAmplitude[startPos:endPos]

    def updateFftGraph(self,_doXYAutorange=True):
        if not self.dataContainer.hasData(): return
        if not self.pqFftWidget.isVisible(): return
        self.pqFftWidget.clear()
        indexes = self.currentGraphIndexes
        if len(indexes) == 0: return
        nr = len(indexes)
        # set some parameters
        signalLen = 2048
        signalLen = signalLen >> self.wGraphFftLength.currentIndex() #2048,1024,512,256
        signalTimeStep = self.dataContainer.dT() #XX 0.0015
        # determine the data window
        npPlotView = self.dataContainer.getNpPlotView(nr)
        x = npPlotView[:,0]
        time = self.pgGraphTimeLine.getPos()[0]
        timeIndex = np.searchsorted(x, time, side="left")
        startIndex = int(timeIndex - signalLen/2)
        #if startIndex>=len(x): startIndex = len(x)-1
        if startIndex+signalLen >= len(x): startIndex = len(x)-signalLen-1
        if startIndex < 0: startIndex = 0
        realSignalLen = len(npPlotView[startIndex:startIndex+signalLen,0])
        # get parameters for fft window
        fftWindow = self.wGraphFftWindow.currentIndex()
        fftOutput = self.wGraphFftOutput.currentText() #0: amplitude, 1: psd
        fftPreFilter = self.wGraphFftPreFilter.currentText() #0: none, 1: average, 2: 1 Hz, 3: 2 Hz, 4; 4 Hz, 5: 8 Hz
        # determine the fft window
        if fftWindow == 1:   win = np.bartlett(realSignalLen)
        elif fftWindow == 2: win = np.blackman(realSignalLen)
        elif fftWindow == 3: win = np.hamming(realSignalLen)
        elif fftWindow == 4: win = np.hanning(realSignalLen)
        elif fftWindow == 5: win = np.kaiser(realSignalLen, pi*2)
        elif fftWindow == 6: win = np.kaiser(realSignalLen, pi*3)
        else: win = None
        # calculate and plot fft curves
        startPos = 0 ##1 #remove f=0
        fftFrequencies = np.fft.rfftfreq( signalLen, d=signalTimeStep )
        endPos = len(fftFrequencies)
        if fftOutput == 'psd (log f)':
            startPos = np.searchsorted( fftFrequencies, 10.0)-1 #15 #remove f<10
            self.pqFftWidget.setLogMode(x=True)
        else:
            self.pqFftWidget.setLogMode(x=False)
        #fftFrequencies = fftFrequencies[startPos:]
        fftRange = self.wFftZoomFactor.currentText()
        if fftRange == '1/2':
            endPos = int(endPos/2)+1
        elif fftRange == '1/3':
            endPos = int(endPos/3)+1
        elif fftRange == '1/4':
            endPos = int(endPos/4)+1
        elif fftRange == '1/5':
            endPos = int(endPos/5)+1
        fftFrequencies = fftFrequencies[startPos:endPos]
        # calculate pre filter
        filt = np.ones(len(fftFrequencies))
        self.applyFilter = False
        if ('Hz' in fftPreFilter) and (fftOutput == 'amplitude'):
            fg = float(fftPreFilter.split(' ')[0]) # get first junk and convert to float
            for fi in range(len(fftFrequencies)):
                f = fftFrequencies[fi]
                fnorm = f / fg
                hpf = fnorm / sqrt( 1.0 + fnorm*fnorm )
                filt[fi] = hpf
                if f <= fg: filt[fi] = 0

            self.applyFilter = True
        # limit to at most 3 fft curves
        nrRange = nr
        if nrRange > 3: nrRange = 3
        for i in range(nrRange):
            signal = npPlotView[startIndex:startIndex+signalLen,indexes[i]]
            if fftPreFilter == 'average':
                # subtract average from data
                signal2 = np.copy(signal)
                signal = signal2
                signal -= signal.mean()
            fftAmplitude = self.calculateFftAmplitude(signal, signalLen, fftWindow, win, startPos, endPos)
            # fftAmplitude and fftFrequencies are of identical length
            if self.applyFilter:
                fftAmplitude = fftAmplitude*filt
            if fftOutput == 'psd (lin f)':
                fftAmplitude = 40*np.log10(np.clip(fftAmplitude,1.0e-24,1.0e24)) #log(x^2) = 2log(x)
            elif fftOutput == 'psd (log f)':
                fftAmplitude = 40*np.log10(np.clip(fftAmplitude,1.0e-24,1.0e24)) #log(x^2) = 2log(x)
            self.pqFftWidget.plot(fftFrequencies, fftAmplitude, pen=(i,nr))
        # auto range as needed
        if self.bFftAutoRange.checkState() == QtCore.Qt.Checked:
            if _doXYAutorange:
                if self.bYAutoRangeOff.checkState() != QtCore.Qt.Checked:
                    self.pqFftWidget.autoRange()
                else:
                    self.pqFftWidget.disableAutoRange()
                    bounds = self.pqFftWidget.vb.childrenBoundingRect(items=None)
                    if bounds is not None:
                        self.pqFftWidget.setXRange(bounds.left(), bounds.right())

    def updateGraphLegend(self, indexes=[]): #indexes indicates also if it should be plotted or not
        nr = len(indexes)
        label = ''
        for i in range(nr):
            col = pg.mkColor( (i,nr) )
            colstr = pg.colorStr(col)[:6]
            label += "<span style='color: #"+colstr+"'>"+self.logItemNameList[indexes[i]] + "</span> , "
        self.wGraphLegend.setText( label[:-3] )

    def updateGraphCursor(self, x=0, y=0):
        self.wGraphCursor.setText( self.wGraphCursorFormatStr % (x,y))

    def updateFftCursor(self, f=0, y=0):
        self.wFftCursor.setText( self.wFftCursorFormatStr % (f,y))

    #is also slot for
    def updateGraphCursorEvent(self, event):
        #event is a QPointF
        if self.pqPlotWidget.sceneBoundingRect().contains(event):
            mousePoint = self.pqPlotWidget.vb.mapSceneToView(event)
            self.updateGraphCursor( mousePoint.x(), mousePoint.y() )
        if self.pqFftWidget.isVisible() and self.pqFftWidget.sceneBoundingRect().contains(event):
            mousePoint = self.pqFftWidget.vb.mapSceneToView(event)
            self.updateFftCursor( mousePoint.x(), mousePoint.y() )

    def updateGraphMaxTimeLabel(self, time=0.0):
        if time < 0.0: time = 0.0
        if time > 4480.0: time = 4480.0
        qtimezero = QtCore.QTime(0,0,0,0)
        qtime = qtimezero.addMSecs(int(time*1000.0))
        self.wGraphMaxTimeLabel.setText( self.wGraphTimeFormatStr % qtime.toString("mm:ss:zzz") )

    def updateGraphTimeLabel(self, time=0.0):
        if time < 0.0: time = 0.0 #this restricts also pos line
        if time > 4480.0: time = 4480.0
        maxtime = self.dataContainer.getMaxTime()
        if time > maxtime: time = maxtime #this restricts also pos line
        qtimezero = QtCore.QTime(0,0,0,0)
        qtime = qtimezero.addMSecs(int(time*1000.0))
        self.wGraphTimeLabel.setText( self.wGraphTimeFormatStr % qtime.toString("mm:ss:zzz") )
        self.pgGraphTimeLine.setPos(time)
        self.updateFftGraph(True)

    def updateGraphTimeSlider(self, time=0.0):
        tindex = int(time/self.dataContainer.dT()) #0.0015)
        if tindex < 0: tindex = 0
        if tindex > self.wGraphTimeSlider.maximum(): tindex = self.wGraphTimeSlider.maximum()
        self.wGraphTimeSlider.blockSignals(True)
        self.wGraphTimeSlider.setValue( tindex ) #emits a updateGraphTimeSliderValueChangedEvent()
        self.wGraphTimeSlider.blockSignals(False)

    def updateGraphTime(self, time=0.0):
        self.updateGraphTimeLabel(time)
        self.updateGraphTimeSlider(time)

    #is also slot for wGraphTimeSlider.valueChanged()
    def updateGraphTimeSliderValueChangedEvent(self,event):
        time = float(event)*self.dataContainer.dT()
        xRange = self.pqPlotWidget.viewRange()[0]
        deltatime = 0.5*( xRange[1] - xRange[0] )
        self.pqPlotWidget.blockSignals(True)
        self.pqPlotWidget.setXRange( time-deltatime, time+deltatime, padding=0.0 ) #emits a updateGraphRangeChangedEvent()
        self.pqPlotWidget.blockSignals(False)
        self.updateGraphTimeLabel(time)

    #is also slot for pqPlotWidget.sigXRangeChanged()
    def updateGraphRangeChangedEvent(self,event):
        xRange = event.viewRange()[0] #is [float,float]
        time = 0.5*( xRange[0] + xRange[1] )
        self.updateGraphTime(time)

    def doGraphZoomFactor(self):
        xRange = self.pqPlotWidget.viewRange()[0]
        time = 0.5*( xRange[0] + xRange[1] )
        bounds = self.pqPlotWidget.vb.childrenBoundingRect(items=None) #is QRectF
        index = self.wGraphZoomFactor.currentText() #['100 %','10 %','1 %','10 s','5 s','1 s','100 ms']
        if(   index == '100 %' ):  deltatime = 0.5*( bounds.right() - bounds.left() )
        elif( index == '10 %' ):   deltatime = 0.05*( bounds.right() - bounds.left() )
        elif( index == '1 %' ):    deltatime = 0.005*( bounds.right() - bounds.left() )
        elif( index == '30 s' ):   deltatime = 15.0
        elif( index == '10 s' ):   deltatime = 5.0
        elif( index == '5 s' ):    deltatime = 2.5
        elif( index == '2 s' ):    deltatime = 1.0
        elif( index == '1 s' ):    deltatime = 0.5
        elif( index == '250 ms' ): deltatime = 0.125
        elif( index == '100 ms' ): deltatime = 0.05
        self.pqPlotWidget.setXRange( time-deltatime, time+deltatime, padding=0.0 ) #emits a signal, which calls updateGraphTime()


    def setGraphControlWidgetsToRecordOn(self):
        self.wGraphControlWidgets.setEnabled(False)
        
    def setGraphControlWidgetsToRecordOff(self):
        self.wGraphControlWidgets.setEnabled(True)

    def setGraphControlWidgetsToDefault(self):
        self.wGraphControlWidgets.setEnabled(True)
        
    #slot for signal clicked from bRecordClear
    def doRecordClearClicked(self):
        self.setLogSourceToUninitialized(False) #don't uncheck rec

    #slot for signal clicked from bRecordStartStop
    def doRecordStartStopClicked(self):
        if not self.serialReaderThread.isRunning():
            self.setLogSourceToRecord() #doesn't do anything if it was already cLOGSOURCE_RECORD before
            self.bSave.setEnabled(False)
            self.actionSave.setEnabled(False)
            self.actionSaveGraphData.setEnabled(False)
            self.actionClear.setEnabled(False)
            self.bRecordClear.setEnabled(False)
            self.bRecordStartStop.setText('Rec Stop')
            self.serialReaderThread.openSerial(self.wRecordComPort.currentPort())
            self.bGraphShowPoints.setCheckState(QtCore.Qt.Unchecked)
            self.uncheckShowFft()  #XX
            self.setGraphControlWidgetsToRecordOn()
            self.dataContainer.setRecordOn(True)
            self.serialReaderThread.start()
        else:
            self.serialReaderThread.cancel()

    #slot for signal finished of cSerialThread
    def serialReaderThreadDone(self):
        self.serialReaderThread.closeSerial()
        if (self.dataContainer.logType != cLOGTYPE_UNINITIALIZED) or (not self.dataContainer.hasData()):
            self.actionClear.setEnabled(True)
            self.bRecordClear.setEnabled(True)
            self.bSave.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionSaveGraphData.setEnabled(True)
        self.bRecordStartStop.setText('Rec Start')
        self.setGraphControlWidgetsToRecordOff()
        self.dataContainer.setRecordOn(False)
        if self.dataContainer.hasData():
            self.updateGraph(None)


    def serialReaderThreadNewDataAvailable(self):
        dataline = self.serialReaderThread.getDataLine()
        self.dataContainer.appendDataLine(dataline)
        self.dataContainer.logType = self.serialReaderThread.getLogType()
        if self.dataContainer.hasData():
            self.updateGraph(True)


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
        if int(settings.value('SYSTEM/LoadTraffic',0)):
            self.bLoadTraffic.setCheckState(QtCore.Qt.Checked)
        if int(settings.value('SYSTEM/SortParameterList',0)):
            self.bSortParameterList.setCheckState(QtCore.Qt.Checked)
        i = 1
        for c in self.calculationDict:
#            if int(settings.value('SYSTEM/Calculation'+str(i)+'Check', defaultValue=0)):
#                c['check'].setCheckState(QtCore.Qt.Checked)
#            else:    
#                c['check'].setCheckState(QtCore.Qt.Unchecked)
            c['value'].setCurrentText( settings.value('SYSTEM/Calculation'+str(i)+'Value', defaultValue='-') )
            c['scale'].setText(settings.value('SYSTEM/Calculation'+str(i)+'Scale', defaultValue='1'))
            c['offset'].setText(settings.value('SYSTEM/Calculation'+str(i)+'Offset', defaultValue='0'))
            i += 1
        if int(settings.value('SYSTEM/SaveOnlySelectedData',0)):
            self.bSaveOnlySelected.setCheckState(QtCore.Qt.Checked)
        if int(settings.value('SYSTEM/SaveDecimated',0)):
            self.bSaveDecimated.setCheckState(QtCore.Qt.Checked)
        self.bSaveDecimatedDecimation.setText(settings.value('SYSTEM/SaveDecimatedDecimation', defaultValue='1'))
        #if( int(settings.value('SYSTEM/GraphShowPoints',0)) ):
        #    self.bGraphShowPoints.setCheckState(QtCore.Qt.Checked)
        p = settings.value('PORT/Port')
        if p: self.wRecordComPort.setCurrentPort( p )

    def writeSettings(self):
        settings = QSettings(IniFileStr, QSettings.IniFormat)
        if self.bLoadTraffic.checkState() == QtCore.Qt.Checked:
            settings.setValue('SYSTEM/LoadTraffic',1)
        else:
            settings.setValue('SYSTEM/LoadTraffic',0)
        if self.bSortParameterList.checkState() == QtCore.Qt.Checked:
            settings.setValue('SYSTEM/SortParameterList',1)
        else:
            settings.setValue('SYSTEM/SortParameterList',0)
        i = 1     
        for c in self.calculationDict:
#            if  c['check'].checkState() == QtCore.Qt.Checked:
#                settings.setValue('SYSTEM/Calculation'+str(i)+'Check', 1)
#            else:
#                settings.setValue('SYSTEM/Calculation'+str(i)+'Check', 0)
            settings.setValue('SYSTEM/Calculation'+str(i)+'Value', c['value'].currentText())
            settings.setValue('SYSTEM/Calculation'+str(i)+'Scale', c['scale'].text())
            settings.setValue('SYSTEM/Calculation'+str(i)+'Offset', c['offset'].text())
            i += 1
        if self.bSaveOnlySelected.checkState() == QtCore.Qt.Checked:
            settings.setValue('SYSTEM/SaveOnlySelectedData',1)
        else:
            settings.setValue('SYSTEM/SaveOnlySelectedData',0)
        if self.bSaveDecimated.checkState() == QtCore.Qt.Checked:
            settings.setValue('SYSTEM/SaveDecimated',1)
        else:
            settings.setValue('SYSTEM/SaveDecimated',0)
        settings.setValue('SYSTEM/SaveDecimatedDecimation', self.bSaveDecimatedDecimation.text())
        if self.bGraphShowPoints.checkState() == QtCore.Qt.Checked:
            settings.setValue('SYSTEM/GraphShowPoints',1)
        else:
            settings.setValue('SYSTEM/GraphShowPoints',0)
        settings.setValue('SYSTEM/Style',appPalette)
        settings.setValue('PORT/Port',self.wRecordComPort.currentPort())
        settings.sync()

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list') and self.loadLogFileIsAllowed():
            t = event.mimeData().text()
            if t.lower().endswith('.ntlog') or t.lower().endswith('.log') or t.lower().endswith('.dat') or t.lower().endswith('.txt'):
                event.accept()
                return
        event.ignore()

    def dropEvent(self, event):
        if self.loadLogFileIsAllowed():
            fn =  event.mimeData().text().replace('file:///','').replace('/','\\')
            self.doLoadLogFile(fn)



###################################################################
# Main()
##################################################################
# potentially useful: https://riverbankcomputing.com/pipermail/pyqt/2009-March/022171.html

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
    
    IniFileStr = os.path.join( os.path.dirname(app.arguments()[0]) , os.path.basename(IniFileStr) )
    
    settings = QSettings(IniFileStr, QSettings.IniFormat)
    appPalette = settings.value('SYSTEM/Style','auto')
    #appPalette = 'Standard'
    if appPalette == 'Fusion':
        QApplication.setStyle(QStyleFactory.create('Fusion'))
    elif appPalette == 'Standard':
        QApplication.setPalette(QApplication.style().standardPalette())
    elif appPalette == 'auto':
        if winScaleEnvironment > 1.9:
            QApplication.setStyle(QStyleFactory.create('Fusion'))
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
    else:
        QApplication.setPalette(QApplication.style().standardPalette())

    # as second step set the WINSCALE
    #  do this by determining the "real" Windows scale form the fonts, and then corricting for the previously set scale
    #  ratio = app.primaryScreen().devicePixelRatio() #works, gives 1.0 or 2.0
    #  ratio = app.devicePixelRatio() #works, gives 1.0 or 2.0
    winScale = 1.0
    winScaleFont = ( 3.0 * QFontInfo(app.font()).pixelSize() )/( 4.0 * QFontInfo(app.font()).pointSizeF() )
    #winScale = float(winScaleFont)/float(winScaleEnvironment)
    winScale = float(winScaleFont)
    if( winScale < 1.0 ): winScale = 1.0

    arg4main = None
    if len(app.arguments())>1: arg4main = app.arguments()[1]
    main = cMain(winScale, appPalette, arg4main)
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





                #swapping numpy columns
                #a) arr[:,[frm, to]] = arr[:,[to, frm]]
                #b) arr[:, 0], arr[:, 1] = arr[:, 1], arr[:, 0].copy()






'''
some facts about the (discrete) FFT:
signal with dt steps a_n -> FFT A_k
i)  signal with dt steps but shifted by one, i.e. a'_n = a_(n+1)
    -> only phase shift of the A_k, FFT A'_k = A_k * exp(-iXX)
ii) signal with dt/2 steps, but zeros in between, i.e. a'_(2n) = a_n, a'_(2n+1) = 0
    -> A'_k gets twice as wide, but spectrum get's duplicated(mirrored) in 2nd half due to periodicity of A_k in k
=>
signal with each data sample doubled produces
* identical spectrum to half the signal with single data sanmples up to half the frequency
* spectrum above half the frequency is mirrored in
=>
4kHz acc signal sampled at 8kHz, only look at spectrum 0-2kHz
'''





'''
        if orientation == 0:
            return [[1,2,3],[1,1,1]]
#define IMU_01(vs,v)  	(vs).x= -(v).y;  (vs).y= +(v).x;  (vs).z= +(v).z;  // +z90°  -y +x +z  = 0b00001 = 1
        if orientation == 1:
            return [[2,1,3],[-1,+1,+1]]
#define IMU_02(vs,v)  	(vs).x= -(v).x;  (vs).y= -(v).y;  (vs).z= +(v).z;  // +z180° -x -y +z  = 0b00010 = 2
        if orientation == 2:
            return [[1,2,3],[-1,-1,+1]]
#define IMU_03(vs,v)  	(vs).x= +(v).y;  (vs).y= -(v).x;  (vs).z= +(v).z;  // +z270° +y -x +z  = 0b00011 = 3
        if orientation == 3:
            return [[2,1,3],[1,-1,+1]]
#define IMU_04(vs,v)  	(vs).x= +(v).y;  (vs).y= +(v).z;  (vs).z= +(v).x;  // +x0°   +y +z +x  = 0b00100 = 4
        if orientation == 4:
            return [[2,3,1],[+1,+1,+1]]
#define IMU_05(vs,v)  	(vs).x= -(v).z;  (vs).y= +(v).y;  (vs).z= +(v).x;  // +x90°  -z +y +x  = 0b00101 = 5
        if orientation == 5:
            return [[3,2,1],[-1,+1,+1]]
#define IMU_06(vs,v)  	(vs).x= -(v).y;  (vs).y= -(v).z;  (vs).z= +(v).x;  // +x180° -y -z +x  = 0b00110 = 6
        if orientation == 6:
            return [[2,3,1],[-1,-1,+1]]
#define IMU_07(vs,v)  	(vs).x= +(v).z;  (vs).y= -(v).y;  (vs).z= +(v).x;  // +x270° +z -y +x  = 0b00111 = 7
        if orientation == 7:
            return [[3,2,1],[1,-1,+1]]
#define IMU_08(vs,v)  	(vs).x= +(v).z;  (vs).y= +(v).x;  (vs).z= +(v).y;  // +y0°   +z +x +y  = 0b01000 = 8
        if orientation == 8:
            return [[3,1,2],[+1,+1,+1]]
#define IMU_09(vs,v)  	(vs).x= -(v).x;  (vs).y= +(v).z;  (vs).z= +(v).y;  // +y90°  -x +z +y  = 0b01001 = 9
        if orientation == 9:
            return [[1,3,2],[-1,+1,+1]]
#define IMU_10(vs,v)  	(vs).x= -(v).z;  (vs).y= -(v).x;  (vs).z= +(v).y;  // +y180° -z -x +y  = 0b01010 = 10
        if orientation == 10:
            return [[3,1,2],[-1,-1,+1]]
#define IMU_11(vs,v)  	(vs).x= +(v).x;  (vs).y= -(v).z;  (vs).z= +(v).y;  // +y270° +x -z +y  = 0b01011 = 11
        if orientation == 11:
            return [[1,3,2],[+1,-1,+1]]
#define IMU_12(vs,v)  	(vs).x= +(v).y;  (vs).y= +(v).x;  (vs).z= -(v).z;  // -z0°   +y +x -z  = 0b10000 = 16
        if orientation == 12:
            return [[2,1,3],[+1,+1,-1]]
#define IMU_13(vs,v)  	(vs).x= -(v).x;  (vs).y= +(v).y;  (vs).z= -(v).z;  // -z90°  -x +y -z  = 0b10001 = 17
        if orientation == 13:
            return [[1,2,3],[-1,+1,-1]]
#define IMU_14(vs,v)  	(vs).x= -(v).y;  (vs).y= -(v).x;  (vs).z= -(v).z;  // -z180° -y -x -z  = 0b10010 = 18
        if orientation == 14:
            return [[2,1,3],[-1,-1,-1]]
#define IMU_15(vs,v)  	(vs).x= +(v).x;  (vs).y= -(v).y;  (vs).z= -(v).z;  // -z270° +x -y -z  = 0b10011 = 19
        if orientation == 15:
            return [[1,2,3],[+1,-1,-1]]
#define IMU_16(vs,v)  	(vs).x= +(v).z;  (vs).y= +(v).y;  (vs).z= -(v).x;  // -x0°   +z +y -x  = 0b10100 = 20
        if orientation == 16:
            return [[3,2,1],[+1,+1,-1]]
#define IMU_17(vs,v)  	(vs).x= -(v).y;  (vs).y= +(v).z;  (vs).z= -(v).x;  // -x90°  -y +z -x  = 0b10101 = 21
        if orientation == 17:
            return [[2,3,1],[-1,+1,-1]]
#define IMU_18(vs,v)  	(vs).x= -(v).z;  (vs).y= -(v).y;  (vs).z= -(v).x;  // -x180° -z -y -x  = 0b10110 = 22
        if orientation == 18:
            return [[3,2,1],[-1,-1,-1]]
#define IMU_19(vs,v)  	(vs).x= +(v).y;  (vs).y= -(v).z;  (vs).z= -(v).x;  // -x270° +y -z -x  = 0b10111 = 23
        if orientation == 0:
            return [[1,2,3],[1,1,1]]
#define IMU_20(vs,v)  	(vs).x= +(v).x;  (vs).y= +(v).z;  (vs).z= -(v).y;  // -y0°   +x +z -y  = 0b11000 = 24
#define IMU_21(vs,v)  	(vs).x= -(v).z;  (vs).y= +(v).x;  (vs).z= -(v).y;  // -y90°  -z +x -y  = 0b11001 = 25
#define IMU_22(vs,v)  	(vs).x= -(v).x;  (vs).y= -(v).z;  (vs).z= -(v).y;  // -y180° -x -z -y  = 0b11010 = 26
#define IMU_23(vs,v)  	(vs).x= +(v).z;  (vs).y= -(v).x;  (vs).z= -(v).y;  // -y270° +z -x -y  = 0b11011 = 27

        return [[1,2,3],[1.0,1.0,1.0]]
'''
