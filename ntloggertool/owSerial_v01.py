# Version v0.1.1 18. Oct. 2022
# int() added to few calls

import re
import subprocess

from PyQt5 import QtCore, QtWidgets, QtSerialPort, QtNetwork
from PyQt5.QtCore import QIODevice
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtNetwork import QTcpSocket, QUdpSocket


###############################################################################
# cRingBuffer
# this is the class to handle a ring buffer
#-----------------------------------------------------------------------------#
class cRingBuffer():
    def __init__(self, size):
        self.writepos = 0
        self.readpos = 0
        self.SIZEMASK = size-1
        self.buf = bytearray(size)

    def putInt(self, c):
        nextpos = ( self.writepos + 1 ) & self.SIZEMASK
        if nextpos != self.readpos: #fifo not full
            self.buf[self.writepos] = c;
            self.writepos = nextpos

    # buf must be a bytearray
    def putBuf(self, buf):
        for c in buf: self.putInt( c )

    def getInt(self):
        if self.writepos != self.readpos: #fifo not empty
            c = self.buf[self.readpos]
            self.readpos = ( self.readpos + 1 ) & self.SIZEMASK
            return c

    def available(self):
        d = self.writepos - self.readpos
        if d < 0: return d + (self.SIZEMASK+1)
        return d

    def free(self):
        d = self.writepos - self.readpos;
        if d < 0: return d + (self.SIZEMASK+1)
        return self.SIZEMASK - d #the maximum is size-1

    def isEmpty(self):
        if self.writepos == self.readpos: return True
        return False

    def isNotFull(self):
        netxpos = ( self.writepos + 1 ) & (selfSIZEMASK)
        if nextpos != self.readpos: return True
        return False

    def flush(self):
        self.writepos = 0
        self.readpos = 0

    def size(self):
        return self.SIZEMASK + 1
        
        
###############################################################################
# cSerialPortComboBox
# this is the class to select a serial COM port
#-----------------------------------------------------------------------------#
class cSerialPortComboBox(QComboBox):

    def __init__(self, _cMain, _cScale=1.0):
        super().__init__(_cMain)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(int(65*_cScale), int(21*_cScale)))
        self.setMaximumSize(QtCore.QSize(int(65*_cScale), int(21*_cScale)))
        self.view().setMinimumWidth(int(160*_cScale))
        self.populateList()

    def key(self,_s):
        return int(_s[3:7])

    def populateList(self):
        availableSerialPortInfoList = QSerialPortInfo().availablePorts()
        availableSerialPortList = []
        for portInfo in availableSerialPortInfoList:
            '''
            print('-')
            print(portInfo)
            print(portInfo.description())
            print(portInfo.portName())
            print(portInfo.serialNumber())
            print(portInfo.productIdentifier())
            print(portInfo.manufacturer())
            print(portInfo.systemLocation()) #unix type port name
            print(portInfo.vendorIdentifier())
            '''
            s = portInfo.portName()
            while len(s)<13: s += ' '
            p = portInfo.description()
            if re.search(r'Virtual COM Port',p):  d = 'Virtual COM Port'
            elif re.search(r'USB Serial Port',p): d = 'USB Serial Port'
            elif re.search(r'Bluetooth',p):       d = 'Bluetooth'
            #elif re.search(r'Standard',p):        d = 'Standard Port'
            else: d = 'Standard'
            availableSerialPortList.append(s+d)
        availableSerialPortList.sort(key=self.key)

        #the idea is from here: http://stackoverflow.com/questions/31868486/list-all-wireless-networks-python-for-pc
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        #results = subprocess.check_output(["netsh", "wlan", "show", "network"], startupinfo=startupinfo)
        #if b'ENSYS NT Logger' in results:
        #    availableSerialPortList.append('ENSYS NT Logger')
        #bug found by rcgroups user fs008
        try:
            results = subprocess.check_output(["netsh", "wlan", "show", "network"], startupinfo=startupinfo)
        except:
            pass
        else:
            if b'ENSYS NT Logger' in results:
                availableSerialPortList.append('ENSYS NT Logger')

        self.clear()
        self.addItems(availableSerialPortList)

    def showPopup(self):
        self.populateList()
        #super(self.__class__, self).showPopup()
        super().showPopup()

    def currentPort(self):
        pn = self.currentText()
        if re.search(r'^ENSYS',pn):
            return pn
        return re.findall(r'COM\d*',pn)[0]

    def itemPort(self,i):
        pn = self.itemText(i)
        if re.search(r'^ENSYS',pn):
            return pn
        return re.findall(r'COM\d*',pn)[0]

    def setCurrentPort(self,_port):
        for i in range(self.count()):
            if _port==self.itemPort(i):
                self.setCurrentIndex(i)
                return


###############################################################################
# cSerialStream
# this is the class to select a serial COM port
#-----------------------------------------------------------------------------#
#cleaned up to only use TCP, as this seems what ENSYS has finally settled for
cTCP_URL = "172.16.0.1"
cTCP_PORT = 7000

class cSerialStream():

    def __init__(self):
        # they all use the fifo
        self.fifo = cRingBuffer( 1024*1024 )

        self.serialIsSocket = False #assume the default

        self.port = QSerialPort()
        self.port.setBaudRate(2000000)
        self.port.setDataBits(8)
        self.port.setParity(QSerialPort.NoParity)
        self.port.setStopBits(1)
        self.port.setFlowControl(QSerialPort.NoFlowControl)
        self.port.setReadBufferSize( 256*1024 )
        self.port.readyRead.connect(self.readPort)

        self.tcp = QTcpSocket()
        self.tcp.setReadBufferSize( 256*1024 )
        self.tcp.readyRead.connect(self.readTcp)

    # signal for QSerialPort
    # readAll is in bytes, fifo needs bytearray
    def readPort(self):
        self.fifo.putBuf( bytearray(self.port.readAll()) )

    # signal for QTcpSocket
    # readAll is in bytes, fifo needs bytearray
    def readTcp(self):
        self.fifo.putBuf( bytearray(self.tcp.readAll()) )

    def openPort(self,portname):
        self.serialIsSocket = False
        self.port.setPortName(portname)
        self.port.open(QIODevice.ReadWrite) #this unfortunatley b?locks the GUI!!!

    def closePort(self):
        self.port.close()

    def openSocket(self):
        self.serialIsSocket = True
        self.tcp.connectToHost(cTCP_URL, cTCP_PORT, QIODevice.ReadWrite ) #QIODevice.ReadWrite is the default
        self.tcp.waitForConnected(500) #waits max 0.5s

    def closeSocket(self):
        self.tcp.close()

    def open(self, portname):
        self.fifo.flush()
        if "ENSYS" in portname:
            self.openSocket()
        else:
            self.openPort(portname)

    def close(self):
        if self.serialIsSocket:
            self.closeSocket()
        else:
            self.closePort()

    def isValid(self):
        if self.serialIsSocket:
            if not self.tcp.isValid(): return False
        else:
            if self.port.error(): return False
        return True

    def bytesAvailable(self):
        return self.fifo.available()

    def readOneByte(self):
        return bytes([self.fifo.getInt()])
                
