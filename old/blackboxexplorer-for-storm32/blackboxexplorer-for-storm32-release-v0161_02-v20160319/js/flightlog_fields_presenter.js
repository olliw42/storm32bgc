"use strict";

function FlightLogFieldPresenter() {
}

(function() {
    var FRIENDLY_FIELD_NAMES = {
        'axisP[all]': 'PID_P',
        'axisP[0]': 'PID_P[roll]',
        'axisP[1]': 'PID_P[pitch]',
        'axisP[2]': 'PID_P[yaw]',
        'axisI[all]': 'PID_I',
        'axisI[0]': 'PID_I[roll]',
        'axisI[1]': 'PID_I[pitch]',
        'axisI[2]': 'PID_I[yaw]',
        'axisD[all]': 'PID_D',
        'axisD[0]': 'PID_D[roll]',
        'axisD[1]': 'PID_D[pitch]',
        'axisD[2]': 'PID_D[yaw]',
        
        'rcCommand[all]': 'rcCommand',
        'rcCommand[0]': 'rcCommand[roll]',
        'rcCommand[1]': 'rcCommand[pitch]',
        'rcCommand[2]': 'rcCommand[yaw]',
        'rcCommand[3]': 'rcCommand[throttle]',
    
        'gyroADC[all]': 'gyro',
        'gyroADC[0]': 'gyro[roll]',
        'gyroADC[1]': 'gyro[pitch]',
        'gyroADC[2]': 'gyro[yaw]',
    
        'accSmooth[all]': 'acc',
        'accSmooth[0]': 'acc[X]',
        'accSmooth[1]': 'acc[Y]',
        'accSmooth[2]': 'acc[Z]',
        
        'magADC[all]': 'mag',
        'magADC[0]': 'mag[X]',
        'magADC[1]': 'mag[Y]',
        'magADC[2]': 'mag[Z]',
    
        'vbatLatest': 'vbat',
        'BaroAlt': 'baro',
        
        'servo[all]': 'servos',
        'servo[5]': 'tail servo',
        
        'heading[all]': 'heading',
        'heading[0]': 'heading[roll]',
        'heading[1]': 'heading[pitch]',
        'heading[2]': 'heading[yaw]',
        
        //End-users prefer 1-based indexing
        'motor[all]': 'motors',
        'motor[0]': 'motor[1]', 'motor[1]': 'motor[2]', 'motor[2]': 'motor[3]', 'motor[3]': 'motor[4]',
        'motor[4]': 'motor[5]', 'motor[5]': 'motor[6]', 'motor[6]': 'motor[7]', 'motor[7]': 'motor[8]',
        
        //Virtual fields
        'axisSum[all]': 'PID_sum',
        'axisSum[0]' : 'PID_sum[roll]',
        'axisSum[1]' : 'PID_sum[pitch]',
        'axisSum[2]' : 'PID_sum[yaw]',
    }, //;
//ow ###################################
        FRIENDLY_FIELD_NAMES_STORM32 = {
        'Imu1[all]': 'Imu1 all',
        'Imu1[0]': 'Imu1 Pitch',
        'Imu1[1]': 'Imu1 Roll',
        'Imu1[2]': 'Imu1 Yaw',

        'Imu2[all]': 'Imu2 all',
        'Imu2[0]': 'Imu2 Pitch',
        'Imu2[1]': 'Imu2 Roll',
        'Imu2[2]': 'Imu2 Yaw',
        
        'PID[all]': 'PID all',
        'PID[0]': 'PID Pitch',
        'PID[1]': 'PID Roll',
        'PID[2]': 'PID Yaw',

        'PIDMot[all]': 'PIDMot all',
        'PIDMot[0]': 'PIDMot Pitch',
        'PIDMot[1]': 'PIDMot Roll',
        'PIDMot[2]': 'PIDMot Yaw',

        'a1[all]': 'Acc1 all',
        'a1[0]': 'Acc1 Pitch',
        'a1[1]': 'Acc1 Roll',
        'a1[2]': 'Acc1 Yaw',

        'g1[all]': 'Gyro1 all',
        'g1[0]': 'Gyro1 Pitch',
        'g1[1]': 'Gyro1 Roll',
        'g1[2]': 'Gyro1 Yaw',
        
        'a2[all]': 'Acc2 all',
        'a2[0]': 'Acc2 Pitch',
        'a2[1]': 'Acc2 Roll',
        'a2[2]': 'Acc2 Yaw',

        'g2[all]': 'Gyro2 all',
        'g2[0]': 'Gyro2 Pitch',
        'g2[1]': 'Gyro2 Roll',
        'g2[2]': 'Gyro2 Yaw',

        'Vmax[all]': 'Vmax all',
        'Vmax[0]': 'Vmax Pitch',
        'Vmax[1]': 'Vmax Roll',
        'Vmax[2]': 'Vmax Yaw',
        
        'Mot[all]': 'Mot all',
        'Mot[0]': 'Mot Pitch',
        'Mot[1]': 'Mot Roll',
        'Mot[2]': 'Mot Yaw',
        
        'Vibe1[all]': 'Vibe1 all',
        'Vibe1[0]': 'Vibe1 Pitch',
        'Vibe1[1]': 'Vibe1 Roll',
        'Vibe1[2]': 'Vibe1 Yaw',
        
        'Vibe2[all]': 'Vibe2 all',
        'Vibe2[0]': 'Vibe2 Pitch',
        'Vibe2[1]': 'Vibe2 Roll',
        'Vibe2[2]': 'Vibe2 Yaw',
        
        'a1raw[all]': 'a1raw all',
        'a1raw[0]': 'a1raw x',
        'a1raw[1]': 'a1raw y',
        'a1raw[2]': 'a1raw z',

        'g1raw[all]': 'g1raw all',
        'g1raw[0]': 'g1raw x',
        'g1raw[1]': 'g1raw y',
        'g1raw[2]': 'g1raw z',
        
        'a2raw[all]': 'a2raw all',
        'a2raw[0]': 'a2raw x',
        'a2raw[1]': 'a2raw y',
        'a2raw[2]': 'a2raw z',

        'g2raw[all]': 'g2raw all',
        'g2raw[0]': 'g2raw x',
        'g2raw[1]': 'g2raw y',
        'g2raw[2]': 'g2raw z',

        'a3raw[all]': 'a3raw all',
        'a3raw[0]': 'a3raw x',
        'a3raw[1]': 'a3raw y',
        'a3raw[2]': 'a3raw z',

        'g3raw[all]': 'g3raw all',
        'g3raw[0]': 'g3raw x',
        'g3raw[1]': 'g3raw y',
        'g3raw[2]': 'g3raw z',

        'R1[all]': 'R1 all',
        'R1[0]': 'R1 x',
        'R1[1]': 'R1 y',
        'R1[2]': 'R1 z',
        },
        firmwareType;
    
    FlightLogFieldPresenter.setFirmwareType = function(type) {
        firmwareType = type;
    };
//ow -----------------------------------
    
    function presentFlags(flags, flagNames) {
        var 
            printedFlag = false,
            i,
            result = "";
        
        i = 0;
        
        while (flags > 0) {
            if ((flags & 1) != 0) {
                if (printedFlag) {
                    result += "|";
                } else {
                    printedFlag = true;
                }
                
                result += flagNames[i];
            }
            
            flags >>= 1;
            i++;
        }
        
        if (printedFlag) {
            return result;
        } else {
            return "0"; //No flags set
        }
    }
    
    function presentEnum(value, enumNames) {
        if (enumNames[value] === undefined)
            return value;
        
        return enumNames[value];
    }

    /**
     * Attempt to decode the given raw logged value into something more human readable, or return an empty string if
     * no better representation is available.
     * 
     * @param fieldName Name of the field
     * @param value Value of the field
     */
    FlightLogFieldPresenter.decodeFieldToFriendly = function(flightLog, fieldName, value) {
        if (value === undefined)
            return "";

//ow ###################################
        if (firmwareType == gFIRMWARE_TYPE_STORM32) {
            switch (fieldName) {
                case 'time':
                    return formatTime(value / 1000, true);
                case 'Voltage':
                    return (value / 1000).toFixed(3) + " V" ;
                case 'State':
                    if (value == 6) return "NORMAL";
                    if (value == 5) return "RELEVEL";
                    if (value == 4) return "MOTOR DIR DETECT";
                    if (value == 3) return "LEVEL";
                    if (value == 2) return "CALIBRATE";
                    if (value == 1) return "SETTLE";
                    if (value == 0) return "STARTUP MOTORS";
                    return "unknown";
                case "T1":
                case "T2":
                case "T3":
                    return (value/340.0 + 36.53).toFixed(2) + "°" ;
            }
            return "";
        }
//ow -----------------------------------
        
        switch (fieldName) {
            case 'time':
                return formatTime(value / 1000, true);
            
            case 'gyroADC[0]':
            case 'gyroADC[1]':
            case 'gyroADC[2]':
                return Math.round(flightLog.gyroRawToDegreesPerSecond(value)) + " deg/s";
                
            case 'accSmooth[0]':
            case 'accSmooth[1]':
            case 'accSmooth[2]':
                return flightLog.accRawToGs(value).toFixed(2) + "g";
            
            case 'vbatLatest':
                return (flightLog.vbatADCToMillivolts(value) / 1000).toFixed(2) + "V" + ", " + (flightLog.vbatADCToMillivolts(value) / 1000 / flightLog.getNumCellsEstimate()).toFixed(2) + "V/cell";
    
            case 'amperageLatest':
                return (flightLog.amperageADCToMillivolts(value) / 1000).toFixed(2) + "A" + ", " + (flightLog.amperageADCToMillivolts(value) / 1000 / flightLog.getNumMotors()).toFixed(2) + "A/motor";
    
            case 'heading[0]':
            case 'heading[1]':
            case 'heading[2]':
                return (value / Math.PI * 180).toFixed(1) + "°";
            
            case 'BaroAlt':
                return (value / 100).toFixed(1) + "m";
            
            case 'flightModeFlags':
                return presentFlags(value, FLIGHT_LOG_FLIGHT_MODE_NAME);
                
            case 'stateFlags':
                return presentFlags(value, FLIGHT_LOG_FLIGHT_STATE_NAME);
                
            case 'failsafePhase':
                return presentEnum(value, FLIGHT_LOG_FAILSAFE_PHASE_NAME);
                
            default:
                return "";
        }
    };
        
    FlightLogFieldPresenter.fieldNameToFriendly = function(fieldName) {
//ow ###################################
// sysConfig is not easily available, thus the method setFirmwareType() has been added, which told the field presenter the firmwareType
        if (firmwareType != gFIRMWARE_TYPE_STORM32) {
            if (FRIENDLY_FIELD_NAMES[fieldName]) {
                return FRIENDLY_FIELD_NAMES[fieldName];
            }
        } else {
            if (FRIENDLY_FIELD_NAMES_STORM32[fieldName]) {
                return FRIENDLY_FIELD_NAMES_STORM32[fieldName];
            }
        }
//ow -----------------------------------

        return fieldName;
    };
})();
