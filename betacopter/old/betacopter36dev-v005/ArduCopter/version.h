#pragma once

#include "ap_version.h"

//OW
//#define THISFIRMWARE "APM:Copter V3.6-dev" //dev version of 2017-08-12
#define THISFIRMWARE "BetaCopter V3.6-dev 005"
//OWEND
#define FIRMWARE_VERSION 3,6,0,FIRMWARE_VERSION_TYPE_DEV

#ifndef GIT_VERSION
#define FIRMWARE_STRING THISFIRMWARE
#else
#define FIRMWARE_STRING THISFIRMWARE " (" GIT_VERSION ")"
#endif

/*
v0.01:
- merged in the 7 files of the PR AP_BattMonitor: UAVCAN support #6527,
  https://github.com/ArduPilot/ardupilot/pull/6527
  this seems to work!
- add GenericBatteryInfo
  dsdl definition simply added to modules\uavcan\dsdl\uavcan\equipment\power
  enable as BattMonitor_TYPE_UAVCAN_GenericBatteryInfo  = 10
 AP_UAVCAN.h: 3x
 AP_UAVCAN.cpp: 6x
 AP_BattMonitor_Backend.h: 1x
 AP_BattMonitor.h: 1x
 AP_BattMonitor.cpp: 1x
 AP_BattMonitor_UAVCAN.h: 2x
 AP_BattMonitor_UAVCAN.cpp: 2x
v0.01-03:
 - flight tested! passed!
v0.02:
 - charge handling for GenericBatteryInfo added
 - flight tested! passed! 2017-08-13
v0.03:
start into uavcan mount
 - 01: first working demo of STorM32 UAVCAN mount, emits NodeSPecific with payload 'Hey'
 - 02: first working version with BP_STorM32 integrated, emits send_attitude()
 - 03:
 - if( charge == NAN ) replaced by if (uavcan::isNaN(charge)) in AP_BattMonitor_UAVCAN.cpp
 - sending arget angles in various formats works
 - storm32.Status works

 - added in_failsafe() to AP_HAL\RCInputs.h and AP_HAL_PX4\RCInputs.h, see https://github.com/ArduPilot/ardupilot/issues/6096
   THIS DOES NOT WORK HOWEVER!
   added copter.in_failsafe_radio() in Copter.h
   THIS DOES NOT WORK HOWEVER!
   neither did do the job
 - flight tested! passed! 2017-08-18
 AP_Mount.h: 3x
 AP_Mount.cpp: 2x
v0.04:
 - send_attitude() added
 - _serial__write() with priority
   STorM32 Link arrives!
 - added serial support, as in "old" betacopter
   serial is MNT_TYPE = 84, and needs SERIALx_PROTOCOL = 84
   can    is MNT_TYPE = 83, and needs appropriate CAN settings
 AP_SerialManager.cpp/.h: 1x each to adopt SerialProtocol_SToRM32_Native = 84
v0.05:
 - camera trigger handling added
   the handling has changed a bit vs AC3.4, but I think it is till correctly placed in AP_Camera::trigger_pic()
   "new" approach to keeping my own variables, I've put them into the copter class, much easier&cleaner
 AP_Camera.cpp: 2x (no change in AP_Camera.h)
 - mode 84 tested on the bench, and it all seems to work
 - flight tested in mode 83! passed! 2017-08-19


ap.in_arming_delay instead of motors.armed() ??
ap.rc_receiver_present for a better "failsafe" handling ??
ap.initialised can this be used to send a banner at the proper time ??
how to detect if connected to a GCS ??


TODO: how to autodetect the presence of a STorM32 gimbal, and/or how to get it's UAVCAN node id
TODO: find_gimbal() also for CAN
TODO: the flags of CircuitStatus an GenericBatteryInfo should be evaluated
 */
