//*****************************************************
//OW
// STorM32 C library to handle serial RC commands
// http://www.olliw.eu/storm32bgc-wiki/Serial_Communication#Serial_Communication_-_RC_Commands
// (c) olliw, www.olliw.eu, GPL3
// version 17. Nov. 2020
//*****************************************************
//
//*****************************************************
// Example usage for CMD_SETANGLES:
//    
// if (_tx_hasspace(sizeof(tSTorM32CmdSetAngles))) {
//   tSTorM32CmdSetSetAngles t;
//   t.pitch = 10.0f;
//   t.roll = 0.0f;
//   t.yaw = 0.0f;
//   t.flags = 0;
//   t.type = 0;
//   storm32_finalize_CmdSetAngles(&t);
//   _write( (uint8_t*)(&t), sizeof(tSTorM32CmdSetAngles) );
// }
//*****************************************************

#pragma once
#ifndef STORM32_LIB_H
#define STORM32_LIB_H // don't assume #pragma once is available

#ifdef __cplusplus
extern "C"
{
#endif


//------------------------------------------------------
// Constants
//------------------------------------------------------

#define STORM32RCCMD_HEADER_LEN             3
#define STORM32RCCMD_CRC_LEN                2
#define STORM32RCCMD_FRAME_LEN              5

// the length of a RCcmd response is at most 77 bytes
#define STORM32RCCMD_RESPONSE_MAXLEN        77


// RCCMD data packets, outgoing to STorM32
enum STORM32RCCMDENUM {
  STORM32RCCMD_GET_VERSIONSTR               = 0x02,
  STORM32RCCMD_GET_DATAFIELDS               = 0x06,
  STORM32RCCMD_SET_PANMODE                  = 0x0D,
  STORM32RCCMD_DO_CAMERA                    = 0x0F,
  STORM32RCCMD_SET_ANGLES                   = 0x11,
  STORM32RCCMD_SET_PITCHROLLYAW             = 0x12,
  STORM32RCCMD_SET_PWMOUT                   = 0x13,
  STORM32RCCMD_SET_INPUTS                   = 0x16,
  STORM32RCCMD_SET_HOMELOCATION             = 0x17,
  STORM32RCCMD_SET_TARGETLOCATION           = 0x18,
  STORM32RCCMD_SET_INPUTCHANNEL             = 0x19,
  STORM32RCCMD_SET_CAMERA                   = 0x1A,
  STORM32RCCMD_ACTIVEPANMODESETTING         = 0x64,
  STORM32RCCMD_STORM32LINKV2                = 0xDA,
};


// STorM32 states
enum STORM32STATEENUM {
  STORM32STATE_STARTUP_MOTORS               = 0,
  STORM32STATE_STARTUP_SETTLE,
  STORM32STATE_STARTUP_CALIBRATE,
  STORM32STATE_STARTUP_LEVEL,
  STORM32STATE_STARTUP_MOTORDIRDETECT,
  STORM32STATE_STARTUP_RELEVEL,
  STORM32STATE_NORMAL,
  STORM32STATE_STARTUP_FASTLEVEL,
};


// flags for reading live data from the STorM32, requested with RCcmd GetDataFields
enum STORM32LIVEDATAENUM {
  STORM32LIVEDATA_STATUS_V1                 = 0x0001,
  STORM32LIVEDATA_TIMES                     = 0x0002,
  STORM32LIVEDATA_IMU1GYRO                  = 0x0004,
  STORM32LIVEDATA_IMU1ACC                   = 0x0008,
  STORM32LIVEDATA_IMU1R                     = 0x0010,
  STORM32LIVEDATA_IMU1ANGLES                = 0x0020,
  STORM32LIVEDATA_PIDCNTRL                  = 0x0040,
  STORM32LIVEDATA_INPUTS                    = 0x0080,
  STORM32LIVEDATA_IMU2ANGLES                = 0x0100,
  STORM32LIVEDATA_MAGANGLES                 = 0x0200,
  STORM32LIVEDATA_STORM32LINK               = 0x0400,
  STORM32LIVEDATA_IMUACCCONFIDENCE          = 0x0800,
  STORM32LIVEDATA_ATTITUDE_RELATIVE         = 0x1000,
  STORM32LIVEDATA_STATUS_V2                 = 0x2000,
  STORM32LIVEDATA_ENCODERANGLES             = 0x4000,
  STORM32LIVEDATA_IMUACCABS                 = 0x8000,
};


enum STORM32PANMODEENUM {
  STORM32PANMODE_OFF                        = 0,
  STORM32PANMODE_HOLDHOLDPAN,
  STORM32PANMODE_HOLDHOLDHOLD,
  STORM32PANMODE_PANPANPAN,
  STORM32PANMODE_PANHOLDHOLD,
  STORM32PANMODE_PANHOLDPAN,
  STORM32PANMODE_HOLDPANPAN,
};


enum STORM32DOCAMERAENUM {
  STORM32DOCAMERA_OFF                       = 0x00,
  STORM32DOCAMERA_SHUTTER                   = 0x01,
  STORM32DOCAMERA_VIDEOON                   = 0x03,
  STORM32DOCAMERA_VIDEOOFF                  = 0x04,
};


enum STORM32LINKFCSTATUSAPENUM {
  STORM32LINK_FCSTATUS_AP_AHRSHEALTHY       = 0x01, // => Q ok, ca. 15 secs
  STORM32LINK_FCSTATUS_AP_AHRSINITIALIZED   = 0x02, // => vz ok, ca. 32 secs
  STORM32LINK_FCSTATUS_AP_GPS3DFIX          = 0x04, // ca 60-XXs
  STORM32LINK_FCSTATUS_AP_NAVHORIZVEL       = 0x08, // comes very late, after GPS fix and few secs after position_ok()
  STORM32LINK_FCSTATUS_AP_ARMED             = 0x40, // tells when copter is about to take-off
  STORM32LINK_FCSTATUS_ISARDUPILOT          = 0x80, // permanently set if it's ArduPilot, so STorM32 knows about and can act accordingly
};


//------------------------------------------------------
// CRC
//------------------------------------------------------
// that's the same as in mavlink/v2.0/checksum.h
// if available, you should include the mavlink version instead of using this here
// you can force using the crc code here by defining STORM32LIB_USE_CRC before including the lib

#if (defined STORM32LIB_USE_CRC) || (!defined MAVLINK_H)

#define X25_INIT_CRC 0xffff

static inline void crc_accumulate(uint8_t data, uint16_t *crcAccum)
{
uint8_t tmp;
  tmp = data ^ (uint8_t)(*crcAccum &0xff);
  tmp ^= (tmp<<4);
  *crcAccum = (*crcAccum>>8) ^ (tmp<<8) ^ (tmp <<3) ^ (tmp>>4);
}


static inline uint16_t crc_calculate(const uint8_t* pBuffer, uint16_t length)
{
uint16_t crcTmp = X25_INIT_CRC;
  while (length--) {
    crc_accumulate(*pBuffer++, &crcTmp);
  }
  return crcTmp;
}

#endif


//------------------------------------------------------
// PACKED
//------------------------------------------------------
// different code bases can have different versions of packed, or none
// if it is not like this, define your own before including this lib

#ifndef STORM32LIBPACKED
#define STORM32LIBPACKED __attribute__((__packed__))
#endif


//------------------------------------------------------
// standard helpers
//------------------------------------------------------

static inline uint16_t storm32_is_normalstate(uint16_t state)
{
  if ((state == STORM32STATE_NORMAL) || (state == STORM32STATE_STARTUP_FASTLEVEL)) return 1;
  return 0;
}


//------------------------------------------------------
// RCCMD  GetVersionStr  #2 = 0x02
//------------------------------------------------------
// has a response
// outgoing: 5 bytes = 434us @ 115200bps

#define STORM32RCCMD_GET_VERSIONSTR_OUTLEN  0x00

struct STORM32LIBPACKED tSTorM32CmdGetVersionStr { // len = 0x00
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t crc;
};

struct STORM32LIBPACKED tSTorM32CmdGetVersionStrAckPayload { // response to CmdGetVersionStr, let's keep just the payload
  char versionstr[16+1]; // 16 chars + 1 to be able to close it with a \0
  char namestr[16+1]; // 16 chars + 1 to be able to close it with a \0
  char boardstr[16+1]; // 16 chars + 1 to be able to close it with a \0
};


static inline void storm32_finalize_CmdGetVersionStr(void* buf)
{
tSTorM32CmdGetVersionStr* t = (tSTorM32CmdGetVersionStr*)buf;

  t->stx = 0xFA; // it doesn't make sense to supress the response
  t->len = 0x00;
  t->cmd = 0x02;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdGetVersionStr)-3);
}


static inline void storm32_finalize_CmdGetVersionStr_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdGetVersionStr(buf);
  *len = sizeof(tSTorM32CmdGetVersionStr);
}


//------------------------------------------------------
// RCCMD  GetDataFields  #6 = 0x06
//------------------------------------------------------
// has a response
// outgoing: 7 bytes = 608us @ 115200bps

#define STORM32RCCMD_GET_DATAFIELDS_OUTLEN  0x02

struct STORM32LIBPACKED tSTorM32CmdGetDataFields { // len = 0x02
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t flags;
  uint16_t crc;
};

struct STORM32LIBPACKED tSTorM32CmdGetDataFieldsAckPayload { // response to CmdGetDataFields, let's keep just the payload
  uint16_t flags;
  struct {
    uint16_t state;
    uint16_t status;
    uint16_t status2;
    uint16_t status3;
    uint16_t performance;
    uint16_t errors;
    uint16_t voltage;
  } livedata_status; // v2
  struct {
    uint32_t time_boot_ms;
    float pitch_deg;
    float roll_deg;
    float yaw_deg;
  } livedata_attitude;
};


static inline void storm32_finalize_CmdGetDataFields(void* buf)
{
tSTorM32CmdGetDataFields* t = (tSTorM32CmdGetDataFields*)buf;

  t->stx = 0xFA; // it doesn't make sense to supress the response
  t->len = 0x02;
  t->cmd = 0x06;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdGetDataFields)-3);
}


static inline void storm32_finalize_CmdGetDataFields_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdGetDataFields(buf);
  *len = sizeof(tSTorM32CmdGetDataFields);
}


//------------------------------------------------------
// RCCMD  SetPanMode  #13 = 0x0D
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 6 bytes = 521us @ 115200bps

#define STORM32RCCMD_SET_PANMODE_OUTLEN       0x01

struct STORM32LIBPACKED tSTorM32CmdSetPanMode { // len = 0x01
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint8_t panmode;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetPanMode(void* buf)
{
tSTorM32CmdSetPanMode* t = (tSTorM32CmdSetPanMode*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x01;
  t->cmd = 0x0D;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetPanMode)-3);
}


static inline void storm32_finalize_CmdSetPanMode_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetPanMode(buf);
  *len = sizeof(tSTorM32CmdSetPanMode);
}


//------------------------------------------------------
// RCCMD  DoCamera  #15 = 0x0F
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 11 bytes = 955us @ 115200bps

#define STORM32RCCMD_DO_CAMERA_OUTLEN       0x06

struct STORM32LIBPACKED tSTorM32CmdDoCamera { // len = 0x06
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


static inline void storm32_finalize_CmdDoCamera(void* buf)
{
tSTorM32CmdDoCamera* t = (tSTorM32CmdDoCamera*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x06;
  t->cmd = 0x0F;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdDoCamera)-3);
}


static inline void storm32_finalize_CmdDoCamera_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdDoCamera(buf);
  *len = sizeof(tSTorM32CmdDoCamera);
}


//------------------------------------------------------
// RCCMD  SetAngles  #17 = 0x11
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 19 bytes = 1650us @ 115200bps

#define STORM32RCCMD_SET_ANGLES_OUTLEN      0x0E

struct STORM32LIBPACKED tSTorM32CmdSetAngles { // len = 0x0E
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


static inline void storm32_finalize_CmdSetAngles(void* buf)
{
tSTorM32CmdSetAngles* t = (tSTorM32CmdSetAngles*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x0E;
  t->cmd = 0x11;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetAngles)-3);
}


static inline void storm32_finalize_CmdSetAngles_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetAngles(buf);
  *len = sizeof(tSTorM32CmdSetAngles);
}


//------------------------------------------------------
// RCCMD  SetPitchRollYaw  #18 = 0x12
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 11 bytes = 955us @ 115200bps

#define STORM32RCCMD_SET_PITCHROLLYAW_OUTLEN    0x06

struct STORM32LIBPACKED tSTorM32CmdSetPitchRollYaw { // len = 0x06
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t pitch;
  uint16_t roll;
  uint16_t yaw;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetPitchRollYaw(void* buf)
{
tSTorM32CmdSetPitchRollYaw* t = (tSTorM32CmdSetPitchRollYaw*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x06;
  t->cmd = 0x12;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetPitchRollYaw)-3);
}


static inline void storm32_finalize_CmdSetPitchRollYaw_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetPitchRollYaw(buf);
  *len = sizeof(tSTorM32CmdSetPitchRollYaw);
}


//------------------------------------------------------
// RCCMD  SetPwmOut  #19 = 0x13
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 7 bytes = 608us @ 115200bps

#define STORM32RCCMD_SET_PWMOUT_OUTLEN    0x02

struct STORM32LIBPACKED tSTorM32CmdSetPwmOut { // len = 0x02
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t pwm;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetPwmOut(void* buf)
{
tSTorM32CmdSetPwmOut* t = (tSTorM32CmdSetPwmOut*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x02;
  t->cmd = 0x13;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetPwmOut)-3);
}


static inline void storm32_finalize_CmdSetPwmOut_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetPwmOut(buf);
  *len = sizeof(tSTorM32CmdSetPwmOut);
}


//------------------------------------------------------
// RCCMD  SetInputs  #22 = 0x16
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 28 bytes = 2431us @ 115200bps

#define STORM32RCCMD_SET_INPUTS_OUTLEN      0x17

struct STORM32LIBPACKED tSTorM32CmdSetInputs { // len = 0x17
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


static inline void storm32_finalize_CmdSetInputs(void* buf)
{
tSTorM32CmdSetInputs* t = (tSTorM32CmdSetInputs*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x17;
  t->cmd = 0x16;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetInputs)-3);
}


static inline void storm32_finalize_CmdSetInputs_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetInputs(buf);
  *len = sizeof(tSTorM32CmdSetInputs);
}


//------------------------------------------------------
// RCCMD  SetHomeTargetLocation  #23, 24 = 0x17, 0x18
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// cmd = 0x17 for home, 0x18 for target
// outgoing: 19 bytes = 1650us @ 115200bps

#define STORM32RCCMD_SET_HOMELOCATION_OUTLEN    0x0E
#define STORM32RCCMD_SET_TARGETLOCATION_OUTLEN  0x0E

struct STORM32LIBPACKED tSTorM32CmdSetHomeTargetLocation { // len = 0x0E
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  int32_t latitude;
  int32_t longitude;
  int32_t altitude; // in cm
  uint16_t status;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetHomeLocation(void* buf)
{
tSTorM32CmdSetHomeTargetLocation* t = (tSTorM32CmdSetHomeTargetLocation*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x0E;
  t->cmd = 0x17;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetHomeTargetLocation)-3);
}


static inline void storm32_finalize_CmdSetHomeLocation_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetHomeLocation(buf);
  *len = sizeof(tSTorM32CmdSetHomeTargetLocation);
}


static inline void storm32_finalize_CmdSetTargetLocation(void* buf)
{
tSTorM32CmdSetHomeTargetLocation* t = (tSTorM32CmdSetHomeTargetLocation*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x0E;
  t->cmd = 0x18;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32CmdSetHomeTargetLocation)-3);
}


static inline void storm32_finalize_CmdSetTargetLocation_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetTargetLocation(buf);
  *len = sizeof(tSTorM32CmdSetHomeTargetLocation);
}


//------------------------------------------------------
// RCCMD  SetInputChannel  #25 = 0x19
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 9 bytes = 781us @ 115200bps

#define STORM32RCCMD_SET_INPUTCHANNEL_OUTLEN    0x04

struct STORM32LIBPACKED tSTorM32SetInputChannel { // len = 0x04
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t channel;
  uint16_t pwm;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetInputChannel(void* buf)
{
tSTorM32SetInputChannel* t = (tSTorM32SetInputChannel*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x04;
  t->cmd = 0x1A;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32SetInputChannel)-3);
}


static inline void storm32_finalize_CmdSetInputChannel_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetInputChannel(buf);
  *len = sizeof(tSTorM32SetInputChannel);
}


//------------------------------------------------------
// RCCMD  SetCamera  #26 = 0x1A
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 9 bytes = 781us @ 115200bps

#define STORM32RCCMD_SET_SETCAMERA_OUTLEN    0x04

struct STORM32LIBPACKED tSTorM32SetCamera { // len = 0x04
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t control;
  uint16_t control2;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetCamera(void* buf)
{
tSTorM32SetCamera* t = (tSTorM32SetCamera*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x04;
  t->cmd = 0x1A;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32SetCamera)-3);
}


static inline void storm32_finalize_CmdSetCamera_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdSetCamera(buf);
  *len = sizeof(tSTorM32SetCamera);
}


//------------------------------------------------------
// RCCMD  ActivePanModeSetting  #100 = 0x62
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 6 bytes = 521us @ 115200bps

#define STORM32RCCMD_ACTIVEPANMODESETTING_OUTLEN    0x01

struct STORM32LIBPACKED tSTorM32ActivePanModeSetting { // len = 0x01
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint8_t activepanmodesetting;
  uint16_t crc;
};


static inline void storm32_finalize_CmdActivePanModeSetting(void* buf)
{
tSTorM32ActivePanModeSetting* t = (tSTorM32ActivePanModeSetting*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x01;
  t->cmd = 0x64;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32ActivePanModeSetting)-3);
}


static inline void storm32_finalize_CmdActivePanModeSetting_(void* buf, uint16_t* len)
{
  storm32_finalize_CmdActivePanModeSetting(buf);
  *len = sizeof(tSTorM32ActivePanModeSetting);
}


//------------------------------------------------------
// RCCMD  STorM32LinkV2  #218 = 0xDA
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 33 bytes = 2865us @ 115200bps

#define STORM32RCCMD_STORM32LINKV2          0x21

struct STORM32LIBPACKED tSTorM32LinkV2 { // len = 0x21
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint8_t seq;
  uint8_t status;
  uint8_t spare;
  int16_t yawratecmd;
  float q0;
  float q1;
  float q2;
  float q3;
  float vx;
  float vy;
  float vz;
  uint16_t crc;
};


static inline void storm32_finalize_STorM32LinkV2(void* buf)
{
tSTorM32LinkV2* t = (tSTorM32LinkV2*)buf;

  t->stx = 0xF9; // 0xF9 to suppress response
  t->len = 0x21;
  t->cmd = 0xDA;
  t->crc = crc_calculate(&(t->len), sizeof(tSTorM32LinkV2)-3);
}


static inline void storm32_finalize_STorM32LinkV2_(void* buf, uint16_t* len)
{
  storm32_finalize_STorM32LinkV2(buf);
  *len = sizeof(tSTorM32LinkV2);
}


//*****************************************************
#ifdef __cplusplus
}
#endif

#endif // STORM32_LIB_H
