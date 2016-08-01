.. _code-overview-adding-a-new-parameter:

======================================
Adding a New Parameter (Code Overview)
======================================

Parameters can either be part of the main code or part of a library.

Adding a parameter to the main code
===================================

**Step #1:** Find a spare slot in the Parameters class's enum in
`Parameters.h <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Parameters.h>`__
and add your new parameter as shown below in red.  Some things to be
careful of:

-  Try to add the parameter close to parameters that share a similar
   function or worst case add to the end of the "Misc" section.
-  Ensure that the section you are adding it to is not full.  You can
   check if the section is full by counting the number of parameters in
   the section and ensuring that the last element is less than the next
   sections first element.  I.e. the Misc section's first parameter is
   #20.  my_new_parameter is #36.  If the next section began at #36 we
   would not be able to add the new parameter here.
-  Do not add a parameter in the middle of a group thus causing the
   slots for existing parameters to change
-  Do not use slots with "deprecated" or "remove" comments beside them
   because some users may still have the defaults for these old
   parameters in their eeprom so your new parameter's default value
   could be set strangely.

::

        enum {
            // Misc
            //
            k_param_log_bitmask = 20,
            k_param_log_last_filenumber,            // *** Deprecated - remove
                                                    // with next eeprom number
                                                    // change
            k_param_toy_yaw_rate,                           // THOR The memory
                                                            // location for the
                                                            // Yaw Rate 1 = fast,
                                                            // 2 = med, 3 = slow

            k_param_crosstrack_min_distance,    // deprecated - remove with next eeprom number change
            k_param_rssi_pin,
            k_param_throttle_accel_enabled,     // deprecated - remove
            k_param_wp_yaw_behavior,
            k_param_acro_trainer,
            k_param_pilot_velocity_z_max,
            k_param_circle_rate,
            k_param_sonar_gain,
            k_param_ch8_option,
            k_param_arming_check_enabled,
            k_param_sprayer,
            k_param_angle_max,
            k_param_gps_hdop_good,          // 35
            k_param_my_new_parameter,       // 36

**Step #2:** Declare the variable within the Parameters class somewhere
below the enum.  Possible types include AP_Int8, AP_Int16, AP_Float,
AP_Int32 and AP_Vector3 (Note: unsigned integers are not currently
supported).  The name of the variable should be the same as the new enum
but with the "k_param\_" prefix removed.

::

            // 254,255: reserved
        };

        AP_Int16        format_version;
        AP_Int8         software_type;

        // Telemetry control
        //
        AP_Int16        sysid_this_mav;
        AP_Int16        sysid_my_gcs;
        AP_Int8         serial3_baud;
        AP_Int8         telem_delay;

        AP_Int16        rtl_altitude;
        AP_Int8         sonar_enabled;
        AP_Int8         sonar_type;       // 0 = XL, 1 = LV,
                                          // 2 = XLL (XL with 10m range)
                                          // 3 = HRLV
        AP_Float        sonar_gain;
        AP_Int8         battery_monitoring;         // 0=disabled, 3=voltage only,
                                                    // 4=voltage and current
        AP_Float        volt_div_ratio;
        AP_Float        curr_amp_per_volt;
        AP_Int16        pack_capacity;              // Battery pack capacity less reserve
        AP_Int8         failsafe_battery_enabled;   // battery failsafe enabled
        AP_Int8         failsafe_gps_enabled;       // gps failsafe enabled
        AP_Int8         failsafe_gcs;               // ground station failsafe behavior
        AP_Int16        gps_hdop_good;              // GPS Hdop value below which represent a good position
        AP_Int16        my_new_parameter;                  // my new parameter's description goes here

**Step #3:** Add the variable declaration to the var_info table in
`Parameters.cpp <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Parameters.cpp>`__

::

        // @Param: MY_NEW_PARAMETER
        // @DisplayName: My New Parameter
        // @Description: A description of my new parameter goes here
        // @Range: -32768 32767
        // @User: Advanced
        GSCALAR(my_new_parameter, "MY_NEW_PARAMETER", MY_NEW_PARAMETER_DEFAULT),

The @Param ~ @User comments are used by the ground station (i.e. Mission
Planner) to display advice to the user and limit the values that the
user may set the parameter to.

The parameter name (i.e. "MY_NEW_PARAMETER") is limited to 16
characters.

**Step #4:** Add the parameters default to
`config.h <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/config.h>`__

::

    #ifndef MY_NEW_PARAMETER_DEFAULT
     # define MY_NEW_PARAMETER_DEFAULT      100     // default value for my new parameter
    #endif

You're done!  The new parameter can be access from the main code (not
the libraries) as g.my_new_parameter.

Adding a parameter to an existing library
=========================================

Parameters can also be added to libraries by following these steps which
use the `AP_Compass <https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Compass>`__
library as an example.

**Step #1:** Add the new class variable to the top level .h file (i.e.
`Compass.h <https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Compass/Compass.h>`__). 
Possible types include AP_Int8, AP_Int16, AP_Float, AP_Int32 and
AP_Vector3f.  Also add the default value you'd like for the parameter
(we will use this in step #2)

::

    #define MY_NEW_PARAM_DEFAULT         100

    class Compass
    {
    public:
        int16_t product_id;                         /// product id
        int16_t mag_x;                      ///< magnetic field strength along the X axis
        int16_t mag_y;                      ///< magnetic field strength along the Y axis
        int16_t mag_z;                      ///< magnetic field strength along the Z axis
        uint32_t last_update;               ///< micros() time of last update
        bool healthy;                               ///< true if last read OK

        /// Constructor
        ///
        Compass();

    protected:
        AP_Int8 _orientation;
        AP_Vector3f _offset;
        AP_Float _declination;
        AP_Int8 _use_for_yaw;                       ///<enable use for yaw calculation
        AP_Int8 _auto_declination;                  ///<enable automatic declination code
        AP_Int16 _my_new_lib_parameter;              /// description of my new parameter
    };

**Step #2:**\ Add the variable to the var_info table in the .cpp file
(i.e. `Compass.cpp <https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Compass/Compass.cpp>`__)
including @Param ~ @Increment comments to allow the GCS to display the
description to the user and to control the min and max values set from
the ground station.  When adding the new parameter be careful that:

    -  The slot (i.e. "9" below) is one higher than the previous
       variable.
    -  the parameter's name (i.e. MY_NEW_P) length is less than 16
       including the object's prefix that will be added.  I.e. the
       compass object's prefix is "COMPASS\_".

::

    const AP_Param::GroupInfo Compass::var_info[] PROGMEM = {
        // index 0 was used for the old orientation matrix

        // @Param: OFS_X
        // @DisplayName: Compass offsets on the X axis
        // @Description: Offset to be added to the compass x-axis values to compensate for metal in the frame
        // @Range: -400 400
        // @Increment: 1

    <snip>

        // @Param: ORIENT
        // @DisplayName: Compass orientation
        // @Description: The orientation of the compass relative to the autopilot board.
        // @Values: 0:None,1:Yaw45,2:Yaw90,3:Yaw135,4:Yaw180,5:Yaw225,6:Yaw270,7:Yaw315,8:Roll180
        AP_GROUPINFO("ORIENT", 8, Compass, _orientation, ROTATION_NONE),

        // @Param: MY_NEW_P
        // @DisplayName: My New Library Parameter
        // @Description: The new library parameter description goes here
        // @Range: -32768 32767
        // @User: Advanced
        AP_GROUPINFO("MY_NEW_P", 9, Compass, _my_new_lib_parameter, MY_NEW_PARAM_DEFAULT),

        AP_GROUPEND
    };

The parameter can be accessed from within the library as
\_my_new_lib_parameter. Note that we made the parameter "protected"
so it cannot be access from outside the class.  If we'd made it public
then it would have been accessible to the main code as well as
"compass._my_new_lib_parameter".
    
Adding parameters to a newly created library
============================================

Parameters can also be added to your own, home-brewed library, e.g. "AP_MyOwnLib". There
is a restriction though, the class must be member of the Copter class. The following steps are 
required, some of which mirror steps described in the above.

Read carefully and respect the comments given in the above for similar steps!.

**Step #1:** `Parameters.h <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Parameters.h>`__:
Find a spare slot in the Parameters class's enum and add your new parameter's toplevel index.

::

        enum {
            <snip>
            
            k_param_arming_check_enabled,
            k_param_sprayer,
            k_param_angle_max,
            k_param_gps_hdop_good,          // 35
            
            k_param_my_own_lib,       // 36

            <snip>

**Step #2:** `Parameters.cpp <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Parameters.cpp>`__:
Since the class is a completely new addition to the code, it needs to be added to
the main vehicle's var_info table. It's order in the var_info table is not important, it is added here to
the end. Below in red where the AP_MyOwnLib class appears.

::

    const AP_Param::Info var_info[] PROGMEM = {
        <snip>

        // @Param: TERRAIN_FOLLOW
        // @DisplayName: Terrain Following use control
        // @Description: This enables terrain following for RTL and LAND flight modes. To use this option TERRAIN_ENABLE must be 1 and the GCS must  support sending terrain data to the aircraft.  In RTL the RTL_ALT will be considered a height above the terrain.  In LAND mode the vehicle will slow to LAND_SPEED 10m above terrain (instead of 10m above home).  This parameter does not affect AUTO and Guided which use a per-command flag to determine if the height is above-home, absolute or above-terrain.
        // @Values: 0:Do Not Use in RTL and Land 1:Use in RTL and Land
        // @User: Standard
        GSCALAR(terrain_follow, "TERRAIN_FOLLOW", 0),

        // @Group: MOLB_
        // @Path: ../libraries/AP_MyOwnLib/AP_MyOwnLib.cpp
        GOBJECT(myownlib, "MOLB_", AP_MyOwnLib),

        AP_VAREND
    };
   
    
**Step #3:** `Copter.h <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Copter.h>`__:
Add your class to the main vehicle class.
    
::

    class Copter : public AP_HAL::HAL::Callbacks {
    public:
        friend class GCS_MAVLINK;
        friend class Parameters;

        Copter(void);

        // HAL::Callbacks implementation.
        void setup() override;
        void loop() override;

    private:
        <snip>
            
        AP_MyOwnLib myownlib;    
        
        <snip>
    
**Step #4:** `Copter.cpp <https://github.com/ArduPilot/ardupilot/blob/master/ArduCopter/Copter.cpp>`__:
Add the constructor of your class to the main vehicle constructor.
    
::

    /*
      constructor for main Copter class
    */
    Copter::Copter(void) :
        DataFlash{FIRMWARE_STRING},
        flight_modes(&g.flight_mode1),
        <snip>
            
        myownlib(),
  
        <snip>

    
**Step #5:** AP_MyNewLib.h: Add the new variables as well as the parameter var_info table in the library .h file. 
Possible parameter types include AP_Int8, AP_Int16, AP_Float, AP_Int32 and
AP_Vector3f. The paramtrers can be in any section, public, private, or protected.
Also add the default value you'd like for the parameter.

::

    #define MY_NEW_PARAM1_DEFAULT         123
    #define MY_NEW_PARAM2_DEFAULT         420

    class AP_MyOwnLib
    {
    public:
        /// Constructor
        AP_MyOwnLib();

        <snip>

        // parameter var table
        static const struct AP_Param::GroupInfo var_info[];

    private:
        <snip>

    protected:

        AP_Int8 _my_new_parameter1;
        AP_Int8 _my_new_parameter2;

    }; //end of class AP_MyOwnLib

**Step #6:** AP_MyNewLib.cpp: Add the new variables to the var_info table in the library .cpp file.
In addition AP_Param::setup_object_defaults(this, var_info) needs to be called in the constructor. 

::

    #include <AP_Param/AP_Param.h>
    
    const AP_Param::GroupInfo AP_MyOwnLib::var_info[] = {
        // @Param: _PARAM1
        // @DisplayName: 
        // @Description: 
        // @Values: 0:None,1:coolnewfunction
        // @User: Standard
        AP_GROUPINFO("_PARAM1", 0, AP_MyOwnLib, _my_new_parameter1, MY_NEW_PARAM1_DEFAULT),

        // @Param: _PARAM2
        // @DisplayName: 
        // @Description: 
        // @Range: -1 1
        // @Increment: 1
        // @User: Advanced
        AP_GROUPINFO("_PARAM2", 1, AP_MyOwnLib, _my_new_parameter2, MY_NEW_PARAM2_DEFAULT),

        AP_GROUPEND
    };
    
    /// Constructor
    AP_MyOwnLib::AP_MyOwnLib()
    {
        AP_Param::setup_object_defaults(this, var_info);

        <snip>
    }

This concludes the procedure. The parameter can now be accessed from within the library or
the main code like any other class variable. 
