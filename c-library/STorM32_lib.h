//*****************************************************
//OW
// (c) olliw, www.olliw.eu, GPL3
//*****************************************************
//
// the largest RCcmd response can be 77
//

#pragma once
#ifndef STORM32_LIB_H
#define STORM32_LIB_H //don't assume #pragma once is available

#ifdef __cplusplus
extern "C"
{
#endif


//------------------------------------------------------
// Constants
//------------------------------------------------------

// RCcmd data packets, outgoing to STorM32
enum STORM32RCCMDENUM {
  STORM32RCCMD_GET_VERSIONSTR               = 0x02,
  STORM32RCCMD_GET_DATAFIELDS               = 0x06,
  STORM32RCCMD_DO_CAMERA                    = 0x0F,
  STORM32RCCMD_SET_ANGLES                   = 0x11,
  STORM32RCCMD_SET_PITCHROLLYAW             = 0x12,
  STORM32RCCMD_SET_INPUTS                   = 0x16,
  STORM32RCCMD_SET_HOMELOCATION             = 0x17,
  STORM32RCCMD_SET_TARGETLOCATION           = 0x18,
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


enum STORM32LINKFCSTATUSAPENUM {
  STORM32LINK_FCSTATUS_AP_AHRSHEALTHY       = 0x01, //=> Q ok, ca. 15 secs
  STORM32LINK_FCSTATUS_AP_AHRSINITIALIZED   = 0x02, //=> vz ok, ca. 32 secs
  STORM32LINK_FCSTATUS_AP_GPS3DFIX          = 0x04, //ca 60-XXs
  STORM32LINK_FCSTATUS_AP_NAVHORIZVEL       = 0x08, //comes very late, after GPS fix and few secs after position_ok()
  STORM32LINK_FCSTATUS_AP_ARMED             = 0x40, //tells when copter is about to take-off
  STORM32LINK_FCSTATUS_ISARDUPILOT          = 0x80, //permanently set, to indicate that it's ArduPilot, so STorM32 knows about and can act accordingly
};


//------------------------------------------------------
// CRC
//------------------------------------------------------
// that's the same as in mavlink/v2.0/checksum.h
// if that is available, you should include the mavlink version instead of using this here

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
// RCCMD  GetVersionStr  0x02
//------------------------------------------------------
// has a response
// outgoing: 5 bytes = 434us @ 115200bps

#define STORM32RCCMD_GET_VERSIONSTR_OUTLEN  0x00

struct STORM32LIBPACKED tSTorM32CmdGetVersionStr { //len = 0x00
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t crc;
};

struct STORM32LIBPACKED tSTorM32CmdGetVersionStrAckPayload { //response to CmdGetVersionStr, let's keep just the payload
  char versionstr[16+1]; //16 chars + 1 to be able to close it with a \0
  char namestr[16+1]; //16 chars + 1 to be able to close it with a \0
  char boardstr[16+1]; //16 chars + 1 to be able to close it with a \0
};


static inline void storm32_finalize_CmdGetVersionStr(void* buf)
{
tSTorM32CmdGetVersionStr* t = (tSTorM32CmdGetVersionStr*)buf;

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  GetDataFields  0x06
//------------------------------------------------------
// has a response
// outgoing: 7 bytes = 608us @ 115200bps

#define STORM32RCCMD_GET_DATAFIELDS_OUTLEN  0x02

struct STORM32LIBPACKED tSTorM32CmdGetDataFields { //len = 0x02
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  uint16_t flags;
  uint16_t crc;
};

struct STORM32LIBPACKED tSTorM32CmdGetDataFieldsAckPayload { //response to CmdGetDataFields, let's keep just the payload
  uint16_t flags;
  struct {
    uint16_t state;
    uint16_t status;
    uint16_t status2;
    uint16_t status3;
    uint16_t performance;
    uint16_t errors;
    uint16_t voltage;
  } livedata_status; //v2
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

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  DoCamera  0x0F
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 11 bytes = 955us @ 115200bps

#define STORM32RCCMD_DO_CAMERA_OUTLEN       0x06

struct STORM32LIBPACKED tSTorM32CmdDoCamera { //len = 0x06
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

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  SetAngles  0x11
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 19 bytes = 1650us @ 115200bps

#define STORM32RCCMD_SET_ANGLES_OUTLEN      0x0E

struct STORM32LIBPACKED tSTorM32CmdSetAngles { //len = 0x0E
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

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  SetPitchRollYaw  0x12
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 11 bytes = 955us @ 115200bps

#define STORM32RCCMD_SET_PITCHROLLYAW_OUTLEN    0x06
    
struct STORM32LIBPACKED tSTorM32CmdSetPitchRollYaw { //len = 0x06
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

  t->stx = 0xF9; //0xFA; //0xF9 to suppress response
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
// RCCMD  SetInputs  0x16
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 28 bytes = 2431us @ 115200bps

#define STORM32RCCMD_SET_INPUTS_OUTLEN      0x17

struct STORM32LIBPACKED tSTorM32CmdSetInputs { //len = 0x17
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

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  SetHomeTargetLocation  0x17, 0x18
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// cmd = 0x17 for home, 0x18 for target
// outgoing: 19 bytes = 1650us @ 115200bps

#define STORM32RCCMD_SET_HOMELOCATION_OUTLEN    0x0E
#define STORM32RCCMD_SET_TARGETLOCATION_OUTLEN  0x0E
    
struct STORM32LIBPACKED tSTorM32CmdSetHomeTargetLocation { //len = 0x0E
  uint8_t stx;
  uint8_t len;
  uint8_t cmd;
  int32_t latitude;
  int32_t longitude;
  int32_t altitude; //in cm //xxxx.x is above sea level in m
  uint16_t status;
  uint16_t crc;
};


static inline void storm32_finalize_CmdSetHomeLocation(void* buf)
{
tSTorM32CmdSetHomeTargetLocation* t = (tSTorM32CmdSetHomeTargetLocation*)buf;

  t->stx = 0xF9; //0xF9 to suppress response
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

  t->stx = 0xF9; //0xF9 to suppress response
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
// RCCMD  STorM32LinkV2  0xDA
//------------------------------------------------------
// only outgoing, has no response (except of an ACK)
// outgoing: 33 bytes = 2865us @ 115200bps

#define STORM32RCCMD_STORM32LINKV2          0x21

struct STORM32LIBPACKED tSTorM32LinkV2 { //len = 0x21
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

  t->stx = 0xF9; //0xF9 to suppress response
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
