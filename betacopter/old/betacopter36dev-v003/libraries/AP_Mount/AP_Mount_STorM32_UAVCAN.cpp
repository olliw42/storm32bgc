#include "AP_Mount_STorM32_UAVCAN.h"
#include <AP_HAL/AP_HAL.h>
#include "../ArduCopter/Copter.h"
#include <GCS_MAVLink/GCS_MAVLink.h>

#include <AP_UAVCAN/AP_UAVCAN.h>


extern const AP_HAL::HAL& hal;
//extern Copter copter;


AP_Mount_STorM32_UAVCAN::AP_Mount_STorM32_UAVCAN(AP_Mount &frontend, AP_Mount::mount_state &state, uint8_t instance) :
    AP_Mount_Backend(frontend, state, instance),
    _initialised(false)
{
    for (uint8_t i = 0; i < MAX_NUMBER_OF_CAN_DRIVERS; i++) {
        _ap_uavcan[i] = nullptr;
    }

    _task_time_last = 0;
    _task_counter = 0;

    _status.pitch_deg = _status.roll_deg = _status.yaw_deg = 0.0f;
    _status_updated = false;

    _target_to_send = false;
    _target_mode_last = MAV_MOUNT_MODE_RETRACT;
}


// init - performs any required initialisation for this instance
void AP_Mount_STorM32_UAVCAN::init(const AP_SerialManager& serial_manager)
{
    set_mode((enum MAV_MOUNT_MODE)_state._default_mode.get()); //set mode to default value set by user via parameter
    _target_mode_last = _state._mode;
}


// update mount position - should be called periodically
void AP_Mount_STorM32_UAVCAN::update()
{
    //is this allowed, or can the fields change to the negative with time ??
    // exit if not initialised, but check for validity of CAN interfaces
    if (!_initialised) {

        if (hal.can_mgr != nullptr) {
            for (uint8_t i = 0; i < MAX_NUMBER_OF_CAN_DRIVERS; i++) {
                if (hal.can_mgr[i] != nullptr) {
                    AP_UAVCAN *ap_uavcan = hal.can_mgr[i]->get_UAVCAN();
                    if (ap_uavcan != nullptr) {
                        _ap_uavcan[i] = ap_uavcan;
                        _initialised = true; //at least one CAN interface is initialized
                        _serial_is_initialised = true;

                        uint8_t nodeid = 71; //parameter? can't this be autodetected?
                        ap_uavcan->register_storm32status_listener_to_node(this, nodeid); //register listener
                    }
                }
            }
        }

        return;
    }

    //we can have a different loop speed, with which we actually send out the target angles
    uint64_t current_time_ms = AP_HAL::millis64();
    if ((current_time_ms - _task_time_last) > 50) { //each message is send at 10Hz

        switch (_task_counter) {
            case 0:
                set_target_angles_bymountmode();
                send_target_angles();
                break;
            case 1:
                send_cmd_setinputs();
                break;
            default:
                _task_counter = 0;
        }
        _task_counter++;
        if( _task_counter >= 2 ) _task_counter = 0;

        _task_time_last = current_time_ms;
    }
}


// set_mode - sets mount's mode
void AP_Mount_STorM32_UAVCAN::set_mode(enum MAV_MOUNT_MODE mode)
{
    // exit immediately if not initialised
    if (!_initialised) {
        return;
    }

    // record the mode change
    _state._mode = mode;
}


// status_msg - called to allow mounts to send their status to GCS using the MOUNT_STATUS message
void AP_Mount_STorM32_UAVCAN::status_msg(mavlink_channel_t chan)
{
    float pitch_deg, roll_deg, yaw_deg;

    get_status_angles_deg(&pitch_deg, &roll_deg, &yaw_deg);

    // MAVLink MOUNT_STATUS: int32_t pitch(deg*100), int32_t roll(deg*100), int32_t yaw(deg*100)
    mavlink_msg_mount_status_send(chan, 0, 0, pitch_deg*100.0f, roll_deg*100.0f, yaw_deg*100.0f);

    // return target angles as gimbal's actual attitude.  To-Do: retrieve actual gimbal attitude and send these instead
//    mavlink_msg_mount_status_send(chan, 0, 0, ToDeg(_angle_ef_target_rad.y)*100, ToDeg(_angle_ef_target_rad.x)*100, ToDeg(_angle_ef_target_rad.z)*100);
}



//------------------------------------------------------
// BP_STorM32_UAVCAN private function
//------------------------------------------------------

void AP_Mount_STorM32_UAVCAN::set_target_angles_bymountmode(void)
{
    uint16_t pitch_pwm, roll_pwm, yaw_pwm;

    //    if (BP_Component_get_param_rctargettype() == bprctarget_radionin){
    bool get_pwm_target_from_radio = false; //true; //false;

    // flag to trigger sending target angles to gimbal
    bool send_ef_target = false;
    bool send_pwm_target = false;

    // update based on mount mode
    enum MAV_MOUNT_MODE mount_mode = get_mode();

    switch (mount_mode) {
        // move mount to a "retracted" position.
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
            if (get_pwm_target_from_radio) {
                get_pwm_target_angles_from_radio(&pitch_pwm, &roll_pwm, &yaw_pwm);
                send_pwm_target = true;
            } else {
                update_targets_from_rc();
                send_ef_target = true;
            }
            if( is_failsafe() ){
                pitch_pwm = roll_pwm = yaw_pwm = 1500;
                _angle_ef_target_rad.y = _angle_ef_target_rad.x = _angle_ef_target_rad.z = 0.0f;
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
        set_target_angles_rad(_angle_ef_target_rad.y, _angle_ef_target_rad.x, _angle_ef_target_rad.z, mount_mode);
    }

    if (send_pwm_target) {
        set_target_angles_pwm(pitch_pwm, roll_pwm, yaw_pwm, mount_mode);
    }
}


void AP_Mount_STorM32_UAVCAN::get_pwm_target_angles_from_radio(uint16_t* pitch_pwm, uint16_t* roll_pwm, uint16_t* yaw_pwm)
{
    get_valid_pwm_from_channel(_state._tilt_rc_in, pitch_pwm);
    get_valid_pwm_from_channel(_state._roll_rc_in, roll_pwm);
    get_valid_pwm_from_channel(_state._pan_rc_in, yaw_pwm);
}


void AP_Mount_STorM32_UAVCAN::get_valid_pwm_from_channel(uint8_t rc_in, uint16_t* pwm)
{
    #define rc_ch(i) RC_Channels::rc_channel(i-1)

    if (rc_in && (rc_ch(rc_in))) {
        *pwm = rc_ch(rc_in)->get_radio_in();
    } else
        *pwm = 1500;
}


void AP_Mount_STorM32_UAVCAN::set_target_angles_deg(float pitch_deg, float roll_deg, float yaw_deg, enum MAV_MOUNT_MODE mount_mode)
{
    _target.deg.pitch = pitch_deg;
    _target.deg.roll = roll_deg;
    _target.deg.yaw = yaw_deg;
    _target.type = angles_deg;
    _target.mode = mount_mode;
    _target_to_send = true; //do last, should not matter, but who knows
}


void AP_Mount_STorM32_UAVCAN::set_target_angles_rad(float pitch_rad, float roll_rad, float yaw_rad, enum MAV_MOUNT_MODE mount_mode)
{
    _target.deg.pitch = ToDeg(pitch_rad);
    _target.deg.roll = ToDeg(roll_rad);
    _target.deg.yaw = ToDeg(yaw_rad);
    _target.type = angles_deg;
    _target.mode = mount_mode;
    _target_to_send = true; //do last, should not matter, but who knows
}


void AP_Mount_STorM32_UAVCAN::set_target_angles_pwm(uint16_t pitch_pwm, uint16_t roll_pwm, uint16_t yaw_pwm, enum MAV_MOUNT_MODE mount_mode)
{
    _target.pwm.pitch = pitch_pwm;
    _target.pwm.roll = roll_pwm;
    _target.pwm.yaw = yaw_pwm;
    _target.type = angles_pwm;
    _target.mode = mount_mode;
    _target_to_send = true; //do last, should not matter, but who knows
}


void AP_Mount_STorM32_UAVCAN::send_target_angles(void)
{
    if (_target.mode <= MAV_MOUNT_MODE_NEUTRAL) { //RETRACT and NEUTRAL
        if (_target_mode_last == _target.mode) {
            // has been done already, skip
        } else {
            // trigger a recenter camera, this clears all internal Remote states
            // the camera does not need to be recentered explicitly, thus break;
            send_cmd_recentercamera();
            _target_mode_last = _target.mode;
        }
        return;
    }

    // update to current mode, to avoid repeated actions on some mount mode changes
    _target_mode_last = _target.mode;

    if (_target.type == angles_pwm) {
        uint16_t pitch_pwm = _target.pwm.pitch;
        uint16_t roll_pwm = _target.pwm.roll;
        uint16_t yaw_pwm = _target.pwm.yaw;

        uint16_t DZ = 10; //_rc_target_pwm_deadzone;

        if (pitch_pwm < 10) pitch_pwm = 1500;
        if (pitch_pwm < 1500-DZ) pitch_pwm += DZ; else if (pitch_pwm > 1500+DZ) pitch_pwm -= DZ; else pitch_pwm = 1500;

        if (roll_pwm < 10) roll_pwm = 1500;
        if (roll_pwm < 1500-DZ) roll_pwm += DZ; else if (roll_pwm > 1500+DZ) roll_pwm -= DZ; else roll_pwm = 1500;

        if (yaw_pwm < 10) yaw_pwm = 1500;
        if (yaw_pwm < 1500-DZ) yaw_pwm += DZ; else if (yaw_pwm > 1500+DZ) yaw_pwm -= DZ; else yaw_pwm = 1500;

        send_cmd_setpitchrollyaw(pitch_pwm, roll_pwm, yaw_pwm);
    }else {
        float pitch_deg = _target.deg.pitch;
        float roll_deg = _target.deg.roll;
        float yaw_deg = _target.deg.yaw;

        //convert from ArduPilot to STorM32 convention
        // this need correction p:-1,r:+1,y:-1
        send_cmd_setangles(-pitch_deg, -roll_deg, -yaw_deg, 0);
    }
}


void AP_Mount_STorM32_UAVCAN::get_status_angles_deg(float* pitch_deg, float* roll_deg, float* yaw_deg)
{
    *pitch_deg = _status.pitch_deg;
    *roll_deg = _status.roll_deg;
    *yaw_deg = _status.yaw_deg;
}


//------------------------------------------------------
// AP_UAVCAN interface to receive message
//------------------------------------------------------

void AP_Mount_STorM32_UAVCAN::handle_storm32status_msg(float pitch_deg, float roll_deg, float yaw_deg)
{
    //the storm32.Status message sends angles in ArduPilot convention, no conversion needed
    _status.pitch_deg = pitch_deg;
    _status.roll_deg = roll_deg;
    _status.yaw_deg = yaw_deg;

    _status_updated = true;
}


//------------------------------------------------------
// BP_STorM32 interface
//------------------------------------------------------

size_t AP_Mount_STorM32_UAVCAN::_serial_txspace(void)
{
    return 1000;
}


size_t AP_Mount_STorM32_UAVCAN::_serial_write(const uint8_t *buffer, size_t size)
{
    for (uint8_t i = 0; i < MAX_NUMBER_OF_CAN_DRIVERS; i++) {
        if (_ap_uavcan[i] != nullptr) {
            _ap_uavcan[i]->storm32_nodespecific_send( (uint8_t*)buffer, size );
        }
    }
    return size;
}


uint16_t AP_Mount_STorM32_UAVCAN::rcin_read(uint8_t ch)
{
//    if( hal.rcin->in_failsafe() )
//    if( copter.in_failsafe_radio() )
//        return 0;
//    else
    //this seems to be zero from startup without transmitter, and failsafe didn't helped at all, so leave it as it is
    return hal.rcin->read(ch);
}


//------------------------------------------------------
// helper
//------------------------------------------------------

bool AP_Mount_STorM32_UAVCAN::is_failsafe(void)
{
    #define rc_ch(i) RC_Channels::rc_channel(i-1)

    uint8_t roll_rc_in = _state._roll_rc_in;
    uint8_t tilt_rc_in = _state._tilt_rc_in;
    uint8_t pan_rc_in = _state._pan_rc_in;

    if (roll_rc_in && (rc_ch(roll_rc_in)) && (rc_ch(roll_rc_in)->get_radio_in() < 700)) return true;
    if (tilt_rc_in && (rc_ch(tilt_rc_in)) && (rc_ch(tilt_rc_in)->get_radio_in() < 700)) return true;
    if (pan_rc_in && (rc_ch(pan_rc_in)) && (rc_ch(pan_rc_in)->get_radio_in() < 700)) return true;

    return false;
}





