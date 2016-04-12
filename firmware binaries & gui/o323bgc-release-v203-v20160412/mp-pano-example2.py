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
# It however sets the target Sys/Comp IDs to that of the STorM32 (Sys/Comp ID 71/67)
# which measn that in case (A) the mavlink messages are passed through by the Pixhawk.
#
# Many thanks go to Michael Oborne for helping me getting this to work!

import clr
import MissionPlanner
clr.AddReference("MAVLink")
import MAVLink

from MAVLink import mavlink_digicam_control_t
from MAVLink import mavlink_mount_configure_t
from MAVLink import mavlink_mount_control_t

digicam = mavlink_digicam_control_t()
mavlink_digicam_control_t.target_system.SetValue(digicam,71)
mavlink_digicam_control_t.target_component.SetValue(digicam,67)
mavlink_digicam_control_t.shot.SetValue(digicam, 1)

mountconfigure = mavlink_mount_configure_t()
mavlink_mount_configure_t.target_system.SetValue(mountconfigure,71)
mavlink_mount_configure_t.target_component.SetValue(mountconfigure,67)

mount = mavlink_mount_control_t()
mavlink_mount_control_t.target_system.SetValue(mount,71)
mavlink_mount_control_t.target_component.SetValue(mount,67)
mavlink_mount_control_t.input_a.SetValue(mount,0)
mavlink_mount_control_t.input_b.SetValue(mount,0)
mavlink_mount_control_t.input_c.SetValue(mount,0)


print 'Start'

#mavlink_mount_configure_t.mount_mode.SetValue(mountconfigure, MAVLink.MAV_MOUNT_MODE.NEUTRAL)
#typecasting is non-trivial, so just play it simple:
mavlink_mount_configure_t.mount_mode.SetValue(mountconfigure, 1)
MAV.sendPacket(mountconfigure)
Script.Sleep(2000) 

mavlink_mount_control_t.input_a.SetValue(mount, -2000)
mavlink_mount_control_t.input_c.SetValue(mount, 5000)
MAV.sendPacket(mount)
Script.Sleep(3000)
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, -2000)
mavlink_mount_control_t.input_c.SetValue(mount, 0)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, -2000)
mavlink_mount_control_t.input_c.SetValue(mount, -5000)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 0)
mavlink_mount_control_t.input_c.SetValue(mount, -5000)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 0)
mavlink_mount_control_t.input_c.SetValue(mount, 0)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 0)
mavlink_mount_control_t.input_c.SetValue(mount, 5000)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 2000)
mavlink_mount_control_t.input_c.SetValue(mount, 5000)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 2000)
mavlink_mount_control_t.input_c.SetValue(mount, 0)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)

mavlink_mount_control_t.input_a.SetValue(mount, 2000)
mavlink_mount_control_t.input_c.SetValue(mount, -5000)
MAV.sendPacket(mount)
Script.Sleep(2000) 
print 'click'
MAV.sendPacket(digicam)


#mavlink_mount_configure_t.mount_mode.SetValue(mountconfigure, MAVLink.MAV_MOUNT_MODE.NEUTRAL)
mavlink_mount_configure_t.mount_mode.SetValue(mountconfigure, 1)
MAV.sendPacket(mountconfigure)
Script.Sleep(500) 

print 'End'