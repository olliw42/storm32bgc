# This script can be used for three situations:
# A) communication channel is connected to the Pixhawk
#    Mission Planner is connected to Pixhawk (Sys/Comp ID 01/01)
# B) communication channel is connected to the Pixhawk
#    Mission Planner is connected to STorM32 (Sys/Comp ID 71/67)
# C) communication channel is connected to the STorM32
#    Mission Planner is connected to STorM32 (Sys/Comp ID 71/67)
#
# Note:
# * AC does NOT support the common messages COMMAND_LONG:DO_MOUNT_CONTROL and COMMAND_LONG:DO_DIGICAM_CONTROL
#   but instead uses the APM specific messages DO_MOUNT_CONTROL and DO_DIGICAM_CONTROL
# * STorM32 DOES support the common messages COMMAND_LONG:DO_MOUNT_CONTROL and COMMAND_LONG:DO_DIGICAM_CONTROL
#   as well as the APM specific messages DO_MOUNT_CONTROL and DO_DIGICAM_CONTROL
#
# This script uses the DO_MOUNT_CONTROL, DO_MOUNT_CONFIGURE, and DO_DIGICAM_CONTROL messages.

import clr
import MissionPlanner
clr.AddReference("MAVLink")
import MAVLink


print 'Start'

MAV.setMountConfigure(MAVLink.MAV_MOUNT_MODE.NEUTRAL, False, False, False)
Script.Sleep(2000) 
MAV.setMountConfigure(MAVLink.MAV_MOUNT_MODE.MAVLINK_TARGETING, False, False, False)


MAV.setMountControl( -2000, 0, 5000, False)
Script.Sleep(3000)
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( -2000, 0, 0, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( -2000, 0, -5000, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 0, 0, -5000, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 0, 0, 0, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 0, 0, 5000, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 2000, 0, 5000, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 2000, 0, 0, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)

MAV.setMountControl( 2000, 0, -5000, False)
Script.Sleep(2000) 
print 'click'
MAV.setDigicamControl(1)


MAV.setMountConfigure(MAVLink.MAV_MOUNT_MODE.NEUTRAL, False, False, False)
Script.Sleep(500) 
MAV.setMountConfigure(MAVLink.MAV_MOUNT_MODE.RC_TARGETING, False, False, False)

print 'End'