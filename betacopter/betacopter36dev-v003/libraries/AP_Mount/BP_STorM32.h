#pragma once

#include <AP_AHRS/AP_AHRS.h>


#define SERIAL_RECEIVE_BUFFER_SIZE      96 //the largest rccmd response can be 77


class BP_STorM32
{

public:
    /// Constructor
    BP_STorM32();
    
    // interface to write and read from a serial stream
    bool _serial_is_initialised;
    virtual size_t _serial_txspace(void){ return 0; }
    virtual size_t _serial_write(const uint8_t *buffer, size_t size){ return 0; }
    // interface to read the raw receiver values
    virtual uint16_t rcin_read(uint8_t ch){ return 0; };

    void send_attitude(const AP_AHRS_TYPE &ahrs);
    void send_cmd_setangles(float pitch_deg, float roll_deg, float yaw_deg, uint16_t flags);
    void send_cmd_setpitchrollyaw(uint16_t pitch, uint16_t roll, uint16_t yaw);
    void send_cmd_recentercamera(void);
    void send_cmd_docamera(uint16_t trigger_value);
    void send_cmd_setinputs(void);
    void send_cmd_sethomelocation(const AP_AHRS_TYPE &ahrs); //?? or should this be const struct Location &current_loc, as in mount???
    void send_cmd_settargetlocation(void);
    void send_cmd_getdatafields(uint16_t flags);
    void send_cmd_getversionstr(void);

protected:

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
