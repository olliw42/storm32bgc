#pragma once

#include "ap_version.h"

//OW
//#define THISFIRMWARE "APM:Copter V3.4-rc1"
#define THISFIRMWARE "BetaCopter V3.4-rc1 011"
//OWEND
#define FIRMWARE_VERSION 3,4,0, FIRMWARE_VERSION_TYPE_RC

#ifndef GIT_VERSION
#define FIRMWARE_STRING THISFIRMWARE
#else
#define FIRMWARE_STRING THISFIRMWARE " (" GIT_VERSION ")"
#endif


/*
BETACOPTER changes:
(search for //OW )

ArduCopter.cpp      : 3x
Copter.cpp          : 1x
Copter.h            : 3x
GCS_Mavlink.cpp     : 2x
version.h

Paramters.h         : 1x k_param_component = 139
Paramters.cpp       : 1x "STORM"


libraries:

AP_Camera/AP_Camera.cpp                 : 2x  //no change in AP_Camera.h

AP_SerialManager/AP_SerialManager.cpp   : 1x
AP_SerialManager/AP_SerialManager.h     : 1x

AP_Mount/AP_Mount.cpp                   : 2x
AP_Mount/AP_Mount.h                     : 3x  + 1x (insignificant) BUG


new libraries:

AP_Mount/BP_Component.cpp
AP_Mount/BP_Component.h

AP_Mount/BP_Mount_Component.cpp
AP_Mount/BP_Mount_Component.h

*/


/*
changes in AP_SerialManager.h/.cpp, choose protocol 83
*/
/*
changes in AP_Camera.cpp, AP_Camera::trigger_pic() calls set_trigger_picture()
*/
/*
changes in AP_Mount.h/.cpp, choose mount type 83
I didn't wanted to duplicate all mount stuff, so I created a new dummy mount type
calls set_mount_control()
*/

