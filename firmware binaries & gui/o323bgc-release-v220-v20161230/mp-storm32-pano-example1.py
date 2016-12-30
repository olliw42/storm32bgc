# This script can be used for three situations:
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
# This script uses the COMMAND_LONG commands, hence it works only for the STorM32.

import clr
import MissionPlanner
clr.AddReference("MAVLink")
import MAVLink


print 'Start'

#MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONFIGURE, MAVLink.MAV_MOUNT_MODE.NEUTRAL, 0, 0, 0, 0, 0, 0);
#typecasting is non-trivial, so just play it simple:
MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONFIGURE, 1, 0, 0, 0, 0, 0, 0);
Script.Sleep(2000) 


MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, -20.0, 0, 50.0, 0, 0, 0, 0);
Script.Sleep(3000)
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, -20.0, 0, 0.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, -20.0, 0, -50.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 0.0, 0, -50.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 0.0, 0, 0.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 0.0, 0, 50.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 20.0, 0, 50.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 20.0, 0, 0.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);

MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONTROL, 20.0, 0, -50.0, 0, 0, 0, 0);
Script.Sleep(2000) 
print 'click'
MAV.doCommand(MAVLink.MAV_CMD.DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0);


#MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONFIGURE, MAVLink.MAV_MOUNT_MODE.NEUTRAL, 0, 0, 0, 0, 0, 0);
#typecasting is non-trivial, so just play it simple:
MAV.doCommand(MAVLink.MAV_CMD.DO_MOUNT_CONFIGURE, 1, 0, 0, 0, 0, 0, 0);Script.Sleep(500) 
print 'End'