// -*- tab-width: 4; Mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*-

#include "AP_Mount_Backend.h"
#include "BP_Mount_Component.h"
#include "BP_Component.h"

extern const AP_HAL::HAL& hal;


/// Constructor
BP_Mount_Component::BP_Mount_Component(AP_Mount &frontend, AP_Mount::mount_state &state, uint8_t instance) :
    AP_Mount_Backend(frontend, state, instance)
{}

// init - performs any required initialisation for this instance
void BP_Mount_Component::init(const AP_SerialManager& serial_manager)
{
    set_mode((enum MAV_MOUNT_MODE)_state._default_mode.get());
}

// update mount position - should be called periodically
// is called by scheduler with 50Hz
// any time management is done implicitly by AB_Component, as it actually does the action
void BP_Mount_Component::update()
{
    uint16_t pitch_pwm, roll_pwm, yaw_pwm;

    // exit immediately if not initialised
    if (!is_initialized()) {
        return;
    }

    // flag to trigger sending target angles to gimbal
    bool send_ef_target = false;
    bool send_pwm_target = false;

    // update based on mount mode
    enum MAV_MOUNT_MODE mount_mode = get_mode();

    switch (mount_mode) {
        // move mount to a "retracted" position.  To-Do: remove support and replace with a relaxed mode?
        case MAV_MOUNT_MODE_RETRACT:
            {
            const Vector3f &target = _state._retract_angles.get();
            _angle_ef_target_rad.x = ToRad(target.x);
            _angle_ef_target_rad.y = ToRad(target.y);
            _angle_ef_target_rad.z = ToRad(target.z);
            send_ef_target = true;
            }
            break;

        // move mount to a neutral position, typically pointing forward
        case MAV_MOUNT_MODE_NEUTRAL:
            {
            const Vector3f &target = _state._neutral_angles.get();
            _angle_ef_target_rad.x = ToRad(target.x);
            _angle_ef_target_rad.y = ToRad(target.y);
            _angle_ef_target_rad.z = ToRad(target.z);
            send_ef_target = true;
            }
            break;

        // point to the angles given by a mavlink message
        case MAV_MOUNT_MODE_MAVLINK_TARGETING:
            // earth-frame angle targets (i.e. _angle_ef_target_rad) should have already been set by a MOUNT_CONTROL message from GCS
            send_ef_target = true;
            break;

        // RC radio manual angle control, but with stabilization from the AHRS
        case MAV_MOUNT_MODE_RC_TARGETING:
            // update targets using pilot's rc inputs
            if (BP_Component_get_param_rctargettype() == bprctarget_radionin){
                get_pwm_targets_from_radio(&pitch_pwm, &roll_pwm, &yaw_pwm);
                send_pwm_target = true;
            } else {
                update_targets_from_rc();
                send_ef_target = true;
            }
            break;

        // point mount to a GPS point given by the mission planner
        case MAV_MOUNT_MODE_GPS_POINT:
            if(_frontend._ahrs.get_gps().status() >= AP_GPS::GPS_OK_FIX_2D) {
                calc_angle_to_location(_state._roi_target, _angle_ef_target_rad, true, true);
                send_ef_target = true;
            }
            break;

        default:
            // we do not know this mode so do nothing
            break;
    }

    // send target angles
    if (send_ef_target) {
        send_target_angles_rad(_angle_ef_target_rad.y, _angle_ef_target_rad.x, _angle_ef_target_rad.z, mount_mode);
    }

    if (send_pwm_target) {
        send_target_angles_pwm(pitch_pwm, roll_pwm, yaw_pwm, mount_mode);
    }
}

// has_pan_control - returns true if this mount can control it's pan (required for multicopters)
bool BP_Mount_Component::has_pan_control() const
{
    return BP_Component_get_param_haspancontrol();
}

// set_mode - sets mount's mode
void BP_Mount_Component::set_mode(enum MAV_MOUNT_MODE mode)
{
    // exit immediately if not initialised
    if (!is_initialized()) {
        return;
    }

    // record the mode change
    _state._mode = mode;
}

// status_msg - called to allow mounts to send their status to GCS using the MOUNT_STATUS message
void BP_Mount_Component::status_msg(mavlink_channel_t chan)
{
    float pitch_deg, roll_deg, yaw_deg;

    get_target_angles_deg(&pitch_deg, &roll_deg, &yaw_deg);

    // MAVLink MOUNT_STATUS: int32_t pitch(deg*100), int32_t roll(deg*100), int32_t yaw(deg*100)
    mavlink_msg_mount_status_send(chan, 0, 0, pitch_deg*100.0f, roll_deg*100.0f, yaw_deg*100.0f);
}



///
void BP_Mount_Component::get_pwm_targets_from_radio(uint16_t* pitch_pwm, uint16_t* roll_pwm, uint16_t* yaw_pwm)
{
    uint8_t roll_rc_in = _state._roll_rc_in;
    uint8_t tilt_rc_in = _state._tilt_rc_in;
    uint8_t pan_rc_in = _state._pan_rc_in;

    get_valid_pwm_from_channel(tilt_rc_in, pitch_pwm);
    get_valid_pwm_from_channel(roll_rc_in, roll_pwm);
    get_valid_pwm_from_channel(pan_rc_in, yaw_pwm);
}

///
inline void BP_Mount_Component::get_valid_pwm_from_channel(uint8_t rc_in, uint16_t* pwm)
{
    #define rc_ch(i) RC_Channel::rc_channel(i-1)

    if (rc_in && (rc_ch(rc_in))) {
        *pwm = rc_ch(rc_in)->get_radio_in();
    } else
        *pwm = 1500;
}



inline bool BP_Mount_Component::is_initialized()
{
    return true; //return BP_Component_is_initialised(); //this handled by AP_Component
}


inline void BP_Mount_Component::send_target_angles_rad(float pitch_rad, float roll_rad, float yaw_rad, enum MAV_MOUNT_MODE mount_mode)
{
    BP_Component_set_mount_control_rad(pitch_rad, roll_rad, yaw_rad, mount_mode);
//BP_Component_uart_write(" SEND ");
}

inline void BP_Mount_Component::send_target_angles_pwm(uint16_t pitch_pwm, uint16_t roll_pwm, uint16_t yaw_pwm, enum MAV_MOUNT_MODE mount_mode)
{
    BP_Component_set_mount_control_pwm(pitch_pwm, roll_pwm, yaw_pwm, mount_mode);
//BP_Component_uart_write(" SEND ");
}

inline void BP_Mount_Component::get_target_angles_deg(float* pitch_deg, float* roll_deg, float* yaw_deg)
{
    BP_Component_get_mount_attitude_deg(pitch_deg, roll_deg, yaw_deg);
}

