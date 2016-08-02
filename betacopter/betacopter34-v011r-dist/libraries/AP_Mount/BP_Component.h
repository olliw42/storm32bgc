// -*- tab-width: 4; Mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*-

/// @file	AP_Component.h
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
    bpangles_deg = 0, //the STorM32 convention are angles in deg, not rad!
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

bool BP_Component_is_initialised();
void BP_Component_set_trigger_picture();
void BP_Component_set_servo(uint8_t channel, uint16_t pwm);
void BP_Component_set_mount_control_deg(float pitch_deg, float roll_deg, float yaw_deg);
void BP_Component_set_mount_control_rad(float pitch_rad, float roll_rad, float yaw_rad);
void BP_Component_set_mount_control_pwm(uint16_t pitch_pwm, uint16_t roll_pwm, uint16_t yaw_pwm);
void BP_Component_get_mount_attitude_rad(float* roll_rad, float* pitch_rad, float* yaw_rad);
void BP_Component_get_mount_attitude_deg(float* roll_deg, float* pitch_deg, float* yaw_deg);
void BP_Component_set_gcs_sendbanner();

enum BPRCTARGETTYPE BP_Component_get_mount_rctargettype();
bool BP_Component_get_mount_haspancontrol();

void BP_Component_uart_write(const char* str); //just for debug purposes



/// @class  STorM32 basis object
/// @brief
class BP_STorM32
{

public:
    /// Constructor
    BP_STorM32(const AP_AHRS_TYPE &ahrs);

    void init(AP_HAL::UARTDriver *uart);

    void send_attitude();
    void send_cmd_setangles(float pitch_deg, float roll_deg, float yaw_deg, uint16_t flags);
    void send_cmd_setpitchrollyaw(uint16_t pitch, uint16_t roll, uint16_t yaw);
    void send_cmd_docamera(uint16_t trigger_value);
    void send_cmd_setinputs();
    void send_cmd_getdatafields(uint16_t flags);
    void send_cmd_getversionstr();

    void receive_reset();
    void do_receive_singlechar();
    void do_receive();
    bool message_received();

protected:

    const AP_AHRS_TYPE &_ahrs;
    AP_HAL::UARTDriver *_uart;
    bool _uart_is_initialised;

    void flush_rx();
    uint16_t rcin_read(uint8_t ch);

    struct PACKED tSTorM32Link { //len = 0x13, cmd = 0xD9
        uint8_t stx;
        uint8_t len;
        uint8_t cmd;
        uint8_t seq;
        uint8_t status;
        uint8_t spare;
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

    struct PACKED tCmdDoCamera { //len = 0x06, cmd = 0xF
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
    tCmdGetDataFieldsAckPayload _datafields;

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
    void do_tick();
    void do_task();

    // parameter var table
    static const struct AP_Param::GroupInfo var_info[];

private:

    uint16_t _status;
    uint16_t _tick_counter;
    uint16_t _task_counter;
    bool _do_task;

    char _firmwaretext[50];

    void find_gimbal();

public:

    AP_Int8 _has_pan_control;
    AP_Int8 _rc_target_type;
    AP_Int16 _rc_target_pwm_deadzone;

}; //end of class BP_Component

