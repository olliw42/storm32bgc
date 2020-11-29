
import time, os, sys, math
import serial
from STorM32_lib import *


uart = "COM23"
uart = "COM21"
#uart = "COM9"
baud = 115200

display = True
#display = False



if len(sys.argv) > 1:
    print(sys.argv[1])
    if sys.argv[1] == '57' or sys.argv[1] == '57600':
        baud = 57600
    if sys.argv[1] == '115' or sys.argv[1] == '115200':
        baud = 115200
    if sys.argv[1] == '921' or sys.argv[1] == '921600':
        baud = 921600


ser = serial.Serial(uart, baud) 
t1Hz_last = time.perf_counter()

pitch = 0.0
pitch_dir = 1.0
yaw = 0.0
yaw_dir = 1.0


while True:

    tnow = time.perf_counter()
    if tnow - t1Hz_last > 1.0:
        t1Hz_last += 1.0
        if display: 
            print('-- 1Hz --')
            
#        cmd = cCMD_GETVERSION(ser)
#        cmd = cCMD_GETVERSIONSTR(ser)
#        cmd = cCMD_SENDCAMERACOMMAND(ser)
#        cmd.setPayload(b'\x01\x02\x03')
#        cmd = cCMD_SETANGLES(ser)
#        cmd.setPayload(pitch,0.0,yaw)
        cmd = cCMD_SETANGLES(ser,pitch,0.0,yaw)
        cmd.send()
        print(">- ", cmd.getCmd())
        if pitch >= 45.0: pitch_dir = -1.0
        if pitch <= -45.0: pitch_dir = 1.0
        pitch += pitch_dir * 15.0
        if yaw >= 45.0: yaw_dir = -1.0
        if yaw <= -45.0: yaw_dir = 1.0
        yaw += yaw_dir * 7.5

    available = ser.in_waiting
    if available > 0:
        c = ser.read(available)
        print("<- ", c)
