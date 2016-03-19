"use strict";

/**
 * This IMU code is used for attitude estimation, and is directly derived from Baseflight's imu.c.
 */

function IMU(copyFrom) {
    // Constants:
    var
        RAD = Math.PI / 180.0,
        
        ROLL = 0,
        PITCH = 1,
        YAW = 2,
        THROTTLE = 3,
    
        X = 0,
        Y = 1,
        Z = 2,
    
    //Settings that would normally be set by the user in MW config:
        gyro_cmpf_factor = 600,
        gyro_cmpfm_factor = 250,

        accz_lpf_cutoff = 5.0,
        magneticDeclination = 2519,
    
        //Calculate RC time constant used in the accZ lpf:
        fc_acc = 0.5 / (Math.PI * accz_lpf_cutoff),
        
        INV_GYR_CMPF_FACTOR = 1.0 / (gyro_cmpf_factor + 1.0),
        INV_GYR_CMPFM_FACTOR = 1.0 / (gyro_cmpfm_factor + 1.0);
    
    // **************************************************
    // Simplified IMU based on "Complementary Filter"
    // Inspired by http://starlino.com/imu_guide.html
    //
    // adapted by ziss_dm : http://www.multiwii.com/forum/viewtopic.php?f=8&t=198
    //
    // The following ideas was used in this project:
    // 1) Rotation matrix: http://en.wikipedia.org/wiki/Rotation_matrix
    //
    // Currently Magnetometer uses separate CF which is used only
    // for heading approximation.
    //
    // **************************************************
    
    function normalizeVector(src, dest) {
        var length = Math.sqrt(src.X * src.X + src.Y * src.Y + src.Z * src.Z);
        
        if (length !== 0) {
            dest.X = src.X / length;
            dest.Y = src.Y / length;
            dest.Z = src.Z / length;
        }
    }
    
    function rotateVector(v, delta) {
        // This does a  "proper" matrix rotation using gyro deltas without small-angle approximation
        var 
            v_tmp = {X:v.X, Y:v.Y, Z:v.Z},
            mat = [[0,0,0],[0,0,0],[0,0,0]],
            cosx, sinx, cosy, siny, cosz, sinz,
            coszcosx, sinzcosx, coszsinx, sinzsinx;
    
        cosx = Math.cos(delta[ROLL]);
        sinx = Math.sin(delta[ROLL]);
        cosy = Math.cos(delta[PITCH]);
        siny = Math.sin(delta[PITCH]);
        cosz = Math.cos(delta[YAW]);
        sinz = Math.sin(delta[YAW]);
    
        coszcosx = cosz * cosx;
        sinzcosx = sinz * cosx;
        coszsinx = sinx * cosz;
        sinzsinx = sinx * sinz;
    
        mat[0][0] = cosz * cosy;
        mat[0][1] = -cosy * sinz;
        mat[0][2] = siny;
        mat[1][0] = sinzcosx + (coszsinx * siny);
        mat[1][1] = coszcosx - (sinzsinx * siny);
        mat[1][2] = -sinx * cosy;
        mat[2][0] = (sinzsinx) - (coszcosx * siny);
        mat[2][1] = (coszsinx) + (sinzcosx * siny);
        mat[2][2] = cosy * cosx;
    
        v.X = v_tmp.X * mat[0][0] + v_tmp.Y * mat[1][0] + v_tmp.Z * mat[2][0];
        v.Y = v_tmp.X * mat[0][1] + v_tmp.Y * mat[1][1] + v_tmp.Z * mat[2][1];
        v.Z = v_tmp.X * mat[0][2] + v_tmp.Y * mat[1][2] + v_tmp.Z * mat[2][2];
    }
    
    // Rotate the accel values into the earth frame and subtract acceleration due to gravity from the result
    function calculateAccelerationInEarthFrame(accSmooth, attitude, acc_1G)
    {
        var 
            rpy = [
                -attitude.roll,
                -attitude.pitch,
                -attitude.heading
            ],
            result = {
                X: accSmooth[0],
                Y: accSmooth[1],
                Z: accSmooth[2]
            };
    
        rotateVector(result, rpy);
    
        result.Z -= acc_1G;
    
        return result;
    }
    
    // Use the craft's estimated roll/pitch to compensate for the roll/pitch of the magnetometer reading 
    function calculateHeading(vec, roll, pitch) {
        var 
            cosineRoll = Math.cos(roll),
            sineRoll = Math.sin(roll),
            cosinePitch = Math.cos(pitch),
            sinePitch = Math.sin(pitch),
        
            headingX = vec.X * cosinePitch + vec.Y * sineRoll * sinePitch + vec.Z * sinePitch * cosineRoll,
            headingY = vec.Y * cosineRoll - vec.Z * sineRoll,
            heading = Math.atan2(headingY, headingX) + magneticDeclination / 10.0 * RAD;
    
        if (heading < 0)
            heading += 2 * Math.PI;
    
        return heading;
    }
    
    /**
     * Using the given raw data, update the IMU state and return the new estimate for the attitude.
     */
    this.updateEstimatedAttitude = function(gyroADC, accSmooth, currentTime, acc_1G, gyroScale, magADC) {
        var 
            accMag = 0,
            deltaTime,
            scale, 
            deltaGyroAngle = [0,0,0];
        
        if (this.previousTime === false) {
            deltaTime = 1;
        } else {
            deltaTime = currentTime - this.previousTime;
        }
        
        scale = deltaTime * gyroScale;
        this.previousTime = currentTime;
        
        // Initialization
        for (var axis = 0; axis < 3; axis++) {
            deltaGyroAngle[axis] = gyroADC[axis] * scale;
        
            accMag += accSmooth[axis] * accSmooth[axis];
        }
        accMag = accMag * 100 / (acc_1G * acc_1G);
    
        rotateVector(this.estimateGyro, deltaGyroAngle);
    
        // Apply complimentary filter (Gyro drift correction)
        // If accel magnitude >1.15G or <0.85G and ACC vector outside of the limit range => we neutralize the effect of accelerometers in the angle estimation.
        // To do that, we just skip filter, as EstV already rotated by Gyro
        if (72 < accMag && accMag < 133) {
            this.estimateGyro.X = (this.estimateGyro.X * gyro_cmpf_factor + accSmooth[0]) * INV_GYR_CMPF_FACTOR;
            this.estimateGyro.Y = (this.estimateGyro.Y * gyro_cmpf_factor + accSmooth[1]) * INV_GYR_CMPF_FACTOR;
            this.estimateGyro.Z = (this.estimateGyro.Z * gyro_cmpf_factor + accSmooth[2]) * INV_GYR_CMPF_FACTOR;
        }
    
        var 
            attitude = {
                roll: Math.atan2(this.estimateGyro.Y, this.estimateGyro.Z),
                pitch: Math.atan2(-this.estimateGyro.X, Math.sqrt(this.estimateGyro.Y * this.estimateGyro.Y + this.estimateGyro.Z * this.estimateGyro.Z))
            };
        
        if (false && magADC) { //TODO temporarily disabled
            rotateVector(this.estimateMag, deltaGyroAngle);
                
            this.estimateMag.X = (this.estimateMag.X * gyro_cmpfm_factor + magADC[0]) * INV_GYR_CMPFM_FACTOR;
            this.estimateMag.Y = (this.estimateMag.Y * gyro_cmpfm_factor + magADC[1]) * INV_GYR_CMPFM_FACTOR;
            this.estimateMag.Z = (this.estimateMag.Z * gyro_cmpfm_factor + magADC[2]) * INV_GYR_CMPFM_FACTOR;
            
            attitude.heading = calculateHeading(this.estimateMag, attitude.roll, attitude.pitch);
        } else {
            rotateVector(this.EstN, deltaGyroAngle);
            normalizeVector(this.EstN, this.EstN);
            attitude.heading = calculateHeading(this.EstN, attitude.roll, attitude.pitch);
        }
        
        return attitude;
    };
    
    if (copyFrom) {
        this.copyStateFrom(copyFrom);
    } else {
        this.reset();
    }
}

IMU.prototype.reset = function() {
    this.estimateGyro = {X: 0, Y: 0, Z: 0};
    this.EstN = {X: 1, Y: 0, Z: 0};
    this.estimateMag = {X: 0, Y: 0, Z: 0};

    this.previousTime = false;
};

IMU.prototype.copyStateFrom = function(that) {
    this.estimateGyro = {
        X: that.estimateGyro.X,
        Y: that.estimateGyro.Y,
        Z: that.estimateGyro.Z
    };
    
    this.estimateMag = {
        X: that.estimateMag.X,
        Y: that.estimateMag.Y,
        Z: that.estimateMag.Z
    };

    this.EstN = {
        X: that.EstN.X,
        Y: that.EstN.Y,
        Z: that.EstN.Z
    };

    this.previousTime = that.previousTime;
};
