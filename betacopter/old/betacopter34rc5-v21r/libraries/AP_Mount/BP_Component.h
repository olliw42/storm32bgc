// -*- tab-width: 4; Mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*-

/// @file	BP_Component.h
/// @brief	Component manager, with EEPROM-backed storage of constants.
#pragma once

#include <AP_HAL/AP_HAL.h>
#include <AP_AHRS/AP_AHRS.h>
#include <AP_Math/AP_Math.h>


/// this is currently organized for a single component
/// it would however better be organized using the frontend/backend concept, as for AP_Mount
/// this should however easily be done at any time later
/// let's first get things working, and then nice later


#define SERIAL_RECEIVE_BUFFER_SIZE      96 //the largest rccmd response can be 77


/// interface friends to be used from outside
enum BPANGLESTYPEENUM {
    bpangles_deg = 0, //the STorM32 convention is angles in deg, not rad!
    bpangles_pwm
};

typedef struct {
    enum BPANGLESTYPEENUM type;
    union {
        struct {
            float pitch;
            float roll;
            float yaw;
        } deg;
        struct {
            uint16_t pitch;
            uint16_t roll;
            uint16_t yaw;
        } pwm;
    };
} tBP_Angles;

enum BPRCTARGETTYPE {
    bprctarget_mount = 0,
    bprctarget_radionin
};

bool BP_Component_is_initialised(void);
void BP_Component_set_trigger_picture(void);
void BP_Component_set_servo(uint8_t channel, uint16_t pwm);
void BP_Component_set_mount_control_deg(float pitch_deg, float roll_deg, float yaw_deg, enum MAV_MOUNT_MODE mount_mode);
void BP_Component_set_mount_control_rad(float pitch_rad, float roll_rad, float yaw_rad, enum MAV_MOUNT_MODE mount_mode);
void BP_Component_set_mount_control_pwm(uint16_t pitch_pwm, uint16_t roll_pwm, uint16_t yaw_pwm, enum MAV_MOUNT_MODE mount_mode);
void BP_Component_get_mount_attitude_rad(float* roll_rad, float* pitch_rad, float* yaw_rad);
void BP_Component_get_mount_attitude_deg(float* roll_deg, float* pitch_deg, float* yaw_deg);
void BP_Component_set_gcs_sendbanner(void);
enum BPRCTARGETTYPE BP_Component_get_param_rctargettype(void);
bool BP_Component_get_param_haspancontrol(void);
bool BP_Component_get_param_fshover(void);

bool BP_Component_get_param_doarmchecks(void);
bool BP_Component_pre_arm_check(bool display_failure);
bool BP_Component_arm_check(bool display_failure);

void BP_Component_uart_write(const char* str); //just for debug purposes



/// @class  STorM32 basis object
/// @brief
class BP_STorM32
{

public:
    /// Constructor
    BP_STorM32(const AP_AHRS_TYPE &ahrs);

    void send_attitude(void);
    void send_cmd_setangles(float pitch_deg, float roll_deg, float yaw_deg, uint16_t flags);
    void send_cmd_setpitchrollyaw(uint16_t pitch, uint16_t roll, uint16_t yaw);
    void send_cmd_recentercamera(void);
    void send_cmd_docamera(uint16_t trigger_value);
    void send_cmd_setinputs(void);
    void send_cmd_sethomelocation(void);
    void send_cmd_settargetlocation(void);
    void send_cmd_getdatafields(uint16_t flags);
    void send_cmd_getversionstr(void);

    void receive_reset(void);
    void do_receive_singlechar(void);
    void do_receive(void);
    bool message_received(void);

protected:

    const AP_AHRS_TYPE &_ahrs;

    // interface to the uart, this emulates a Stream and is to make class independent on any AP specifics
    bool _uart_is_initialised;
    void _uart_init(bool is_initialized);

    virtual size_t _uart_txspace(void){ return 0; }
    virtual size_t _uart_write(uint8_t){ return 0; }
    virtual size_t _uart_write(const uint8_t *buffer, size_t size){ return 0; }
    virtual uint32_t _uart_available(void){ return 0; }
    virtual uint16_t _uart_read(void){ return 0; }
    // interface to read the raw receiver values
    virtual uint16_t _rcin_read(uint8_t ch){ return 0; };

    void flush_rx(void);
    uint16_t rcin_read(uint8_t ch);

    struct PACKED tSTorM32Link { //len = 0x15, cmd = 0xD9
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint8_t seq;
        uint8_t status;
        uint8_t spare;
        int16_t yawratecmd;
        float q1;
        float q2;
        float q3;
        float q4;
        uint16_t crc;
    };
    uint8_t _storm32link_seq;

    struct PACKED tCmdSetAngles { //len = 0x0E, cmd = 0x011
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        float pitch;
        float roll;
        float yaw;
        uint8_t flags;
        uint8_t type;
        uint16_t crc;
    };

    struct PACKED tCmdSetPitchRollYaw { //len = 0x06, cmd = 0x12
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint16_t pitch;
        uint16_t roll;
        uint16_t yaw;
        uint16_t crc;
    };

    struct PACKED tCmdDoCamera { //len = 0x06, cmd = 0x0F
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint8_t dummy1;
        uint8_t camera_cmd;
        uint8_t dummy2;
        uint8_t dummy3;
        uint8_t dummy4;
        uint8_t dummy5;
        uint16_t crc;
    };

    struct PACKED tCmdSetInputs { //len = 0x17, cmd = 0x16
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint16_t channel0  : 11;  // 176 bits of data (11 bits per channel * 16 channels) = 22 bytes.
        uint16_t channel1  : 11;  //
        uint16_t channel2  : 11;
        uint16_t channel3  : 11;
        uint16_t channel4  : 11;
        uint16_t channel5  : 11;
        uint16_t channel6  : 11;
        uint16_t channel7  : 11;
        uint16_t channel8  : 11;
        uint16_t channel9  : 11;
        uint16_t channel10 : 11;
        uint16_t channel11 : 11;
        uint16_t channel12 : 11;
        uint16_t channel13 : 11;
        uint16_t channel14 : 11;
        uint16_t channel15 : 11;
        uint8_t status;           // 0x01: reserved1, 0x02: reserved2, 0x04: signal loss, 0x08: failsafe
        uint16_t crc;
    };

    struct PACKED tCmdSetHomeTargetLocation { //len = 0x0E, cmd = 0x17 for home, 0x18 for target
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        int32_t latitude;
        int32_t longitude;
        int32_t altitude; //in cm //xxxx.x is above sea level in m
        uint16_t status;
        uint16_t crc;
    };

    struct PACKED tCmdGetVersionStr { //len = 0x00, cmd = 0x02
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint16_t crc;
    };

    struct PACKED tCmdGetVersionStrAckPayload {
        char versionstr[16];
        char namestr[16];
        char boardstr[16];
    };

    struct PACKED tCmdGetDataFields { //len = 0x02, cmd = 0x06
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint16_t flags;
        uint16_t crc;
    };

    struct PACKED tCmdGetDataFieldsAckPayload {
        uint16_t flags;
        struct {
            uint16_t state;
            uint16_t status;
            uint16_t status2;
            uint16_t errors;
            uint16_t voltage;
        } livedata_status;
        struct {
            uint32_t time_boot_ms;
            float pitch_deg;
            float roll_deg;
            float yaw_deg;
        } livedata_attitude;
    };

    typedef struct {
        uint16_t state;
        uint16_t payload_cnt; //counter
        // rccmd message fields, without crc
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        union {
            uint8_t buf[SERIAL_RECEIVE_BUFFER_SIZE+8]; //have some overhead
            tCmdGetDataFieldsAckPayload getdatafields;
            tCmdGetVersionStrAckPayload getversionstr;
        };
    } tSerial;
    tSerial _serial;

}; //end of class BP_STorM32



/// @class  Component
/// @brief
class BP_Component : BP_STorM32
{

public:
    /// Constructor
    BP_Component(const AP_AHRS_TYPE &ahrs);

    void init(const AP_SerialManager& serial_manager);
    void do_tick(void);
    void do_task(void);

    // parameter var table
    static const struct AP_Param::GroupInfo var_info[];

private:

    AP_HAL::UARTDriver *_uart;
    virtual size_t _uart_txspace(void){ return (size_t)_uart->txspace(); }
    virtual size_t _uart_write(uint8_t c){ return _uart->write(c); }
    virtual size_t _uart_write(const uint8_t *buffer, size_t size){ return _uart->write(buffer, size); }
    virtual uint32_t _uart_available(void){ return _uart->available(); }
    virtual uint16_t _uart_read(void){ return _uart->read(); }

    virtual uint16_t _rcin_read(uint8_t ch);

    uint16_t _status;
    uint16_t _tick_counter;
    uint16_t _task_counter;
    bool _do_task;
    enum MAV_MOUNT_MODE _mount_mode_last; //this is to track mount mode changes

    struct tFlags {
        uint16_t gcs_has_been_detected : 1; //this is to indicate that the message is out already
        uint16_t vehicle_has_passed_prearm_checks : 1; //this is to indicate that the message is out already
        uint16_t vehicle_has_been_armed : 1; //this is to indicate that the message is out already
        uint16_t mount_has_been_armed : 1;  //this is to indicate that the message is out already
        uint16_t mount_is_armed : 1;
    };
    tFlags _flags;

    char _firmwaretext[50];

    void find_gimbal(void);
    void handle_do_mount_control_is_set(void);

public:

    // parameter variables
    AP_Int16 _has_pan_control;
    AP_Int16 _rc_target_type;
    AP_Int16 _rc_target_pwm_deadzone;
    AP_Int16 _do_arm_checks;
    AP_Int16 _fs_hover;
    AP_Int16 _disabled_bitmask;

}; //end of class BP_Component

