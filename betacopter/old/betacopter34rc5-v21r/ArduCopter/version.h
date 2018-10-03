#pragma once

#include "ap_version.h"

//OW
//#define THISFIRMWARE "APM:Copter V3.4-rc5" //15.Sep.2016
#define THISFIRMWARE "BetaCopter V3.4-rc5 v0.21"
//OWEND
#define FIRMWARE_VERSION 3,4,0,FIRMWARE_VERSION_TYPE_RC

#ifndef GIT_VERSION
#define FIRMWARE_STRING THISFIRMWARE
#else
#define FIRMWARE_STRING THISFIRMWARE " (" GIT_VERSION ")"
#endif

/*
v0.14:
 - code added to BP_Component::update() to handle MAV_MOUNT_MODE_RETRACT,MAV_MOUNT_MODE_NEUTRAL only once
 - execute a recenter camera when switched into MAV_MOUNT_MODE_RETRACT,MAV_MOUNT_MODE_NEUTRAL mode
=>git v014-02
 - storm32 is NORMAL message
 - everything prepared for prearm and arm checks
 - mount is now enabled along with SERIALx_PROTOCOL=83, MNT_TYPE is then ignored
=>git v014-06
=> v0.15 => git v015 released
v0.15.1:
 - cleaning up comments and formatting
v0.16:
 - prearm passed message is send to GCS
 - ideas to inform STorM32 about arming intention, see .cpp
 - extend FA storm32link with yawratecmd
 - FS_THR_ENABLE = FS_THR_ENABLED_HOVER = 83
v0.17:
 - transfered to 34rc2
 - bug: in MAV_MOUNT_MODE_RETRACT, MAV_MOUNT_MODE_NEUTRAL handling
 - there is no need to think further about arming intention,
   since according to the release notes motor spool up is delayed by 2 secs (needs testing!!!)(yes, is in he code: motors_output())
 - vehicle armed debug message
 - remove FS_THR_ENABLED_HOVER case, introduced STORM_FS_HOVER parameter instead
 - STORM_DIS_MASK bitmask parameter allows to disable options, such as mount, camera, virtual
=> v0.17 => git v017 released 8.Aug.2016
v0.18:
 - flag to disable STorM32-Link added, 128
=> git v018 01
 - separate Stream class from STorM32 class, to make STorM32 class independent on AP specific stuff
v0.19:
 - transfered to 34rc4
 - prearm and arm checks simplified into one function call
v0.20:
 - transfered to 34rc5
v0.21:
 - bug: taskmanager did too many steps
 - CMD_SETHOMELOCATION, CMD_SETTARGETLOCATION added
 - task time upgrade to 10 Hz, performance check with NT logger looked quite good
 */


/*
BETACOPTER changes:
(search for //OW )

version.h
ArduCopter.cpp      : 3x
Copter.cpp          : 1x
Copter.h            : 3x
GCS_Mavlink.cpp     : 2x

Paramters.cpp       : 1x "STORM"
Paramters.h         : 1x k_param_component = 139

arming_checks.cpp   : 4x


events.cpp          : 2x in failsafe_radio_on_event()
radio.cpp           : 1x in read_radio()


libraries:

AP_Camera/AP_Camera.cpp                 : 2x  //no change in AP_Camera.h

AP_SerialManager/AP_SerialManager.cpp   : 1x
AP_SerialManager/AP_SerialManager.h     : 1x

AP_Mount/AP_Mount.cpp                   : 2x
AP_Mount/AP_Mount.h                     : 2x  + 1x (insignificant) BUG


new libraries:

AP_Mount/BP_Component.cpp               OK
AP_Mount/BP_Component.h                 OK

AP_Mount/BP_Mount_Component.cpp         OK
AP_Mount/BP_Mount_Component.h           OK
*/


/*
changes in AP_SerialManager.h/.cpp, choose protocol 83
*/
/*
changes in AP_Camera.cpp, AP_Camera::trigger_pic() calls set_trigger_picture()
*/
/*
changes in AP_Mount.h/.cpp
I didn't wanted to duplicate all mount stuff, so I created a new dummy mount type
*/
/*
changes to correct/improve radio failsafe, choose FS_THR_ENABLE = FS_THR_ENABLED_HOVER (= 83)

this corrects a serious, safety related BUG
was raised in https://groups.google.com/forum/#!topic/drones-discuss/ScdLmLzj6OY, but obviously considered irrelevant by the AP team

when the spektrum satellite has a failsafe, ALL channels are zero, which makes it that the last values are kept
this is very dangerous, it is much better to put the vehicle into a hover situation
note that AP's low throttle value method fails here and can't be used
furthermore, the failsafe is not reported&displayed when disarmed

how to get Mission Planner to display/report the radio failsafe changes?
this way of doing it is not fully satisfying,
  since with failsafe_throttle == FS_THR_DISABLED a radio failsafe is still neither detected nor logged
  but that's what APM wants, so use new option to stay compatible
how to avoid that "wrong" FS_THR_ENABLED values produce nonsense behavior????
these two things are related, and come from the fact that not all situations are handled within failsafe_radio_on_event()

CHECK: channels values are centered irrespective of mode, does this affect Land, RTL, Auto?
CHECK: handling of FS_THR_ENABLED_HOVER in AUTO mode correct? maybe OK for the moment as it is
CHECK: ensure that failsafe is possible only when radio was detected at least once, to prevent startup issues. How??
DECIDE: for ACRO is centering really worthwhile? copter wouldn't stop, maybe doesn't matter as it goes astray anyhow
*/
