"use strict";

function makeReadOnly(x) {
    // Make read-only if browser supports it:
    if (Object.freeze) {
        return Object.freeze(x);
    }
    
    // Otherwise a no-op
    return x;
}

var 
    FlightLogEvent = makeReadOnly({
        SYNC_BEEP: 0,
        
        AUTOTUNE_CYCLE_START: 10,
        AUTOTUNE_CYCLE_RESULT: 11,
        AUTOTUNE_TARGETS: 12,
        INFLIGHT_ADJUSTMENT: 13,
        LOGGING_RESUME: 14,
        
        GTUNE_CYCLE_RESULT: 20,
        
        LOG_END: 255
    }),
    
    FLIGHT_LOG_FLIGHT_MODE_NAME = makeReadOnly([
        "ANGLE_MODE",
        "HORIZON_MODE",
        "MAG",
        "BARO",
        "GPS_HOME",
        "GPS_HOLD",
        "HEADFREE",
        "AUTOTUNE",
        "PASSTHRU",
        "SONAR"
    ]),

    FLIGHT_LOG_FLIGHT_STATE_NAME = makeReadOnly([
        "GPS_FIX_HOME",
        "GPS_FIX",
        "CALIBRATE_MAG",
        "SMALL_ANGLE",
        "FIXED_WING"
    ]),
    
    FLIGHT_LOG_FAILSAFE_PHASE_NAME = makeReadOnly([
        "IDLE",
        "RX_LOSS_DETECTED",
        "LANDING",
        "LANDED"
    ]);
