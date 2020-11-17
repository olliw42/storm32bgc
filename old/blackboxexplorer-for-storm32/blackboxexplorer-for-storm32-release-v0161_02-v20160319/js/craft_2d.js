"use strict";

function Craft2D(flightLog, canvas, propColors, craftParameters) {
    var
        ARM_THICKNESS_MULTIPLIER = 0.18,
        ARM_EXTEND_BEYOND_MOTOR_MULTIPLIER = 1.1,
        
        CENTRAL_HUB_SIZE_MULTIPLIER = 0.3,
        
        MOTOR_LABEL_SPACING = 10,
    
        numMotors = propColors.length, 
        shadeColors = [],

        craftColor = "rgb(76,76,76)",
        
        armLength, bladeRadius;

    function makeColorHalfStrength(color) {
        color = parseInt(color.substring(1), 16);
        
        return "rgba(" + ((color >> 16) & 0xFF) + "," + ((color >> 8) & 0xFF) + "," + (color & 0xFF) + ",0.5)";
    }
    
    this.render = function(canvasContext, frame, frameFieldIndexes) {
        var 
            motorIndex,
            sysConfig = flightLog.getSysConfig();
        
        //Draw arms
        canvasContext.lineWidth = armLength * ARM_THICKNESS_MULTIPLIER;
        
        canvasContext.lineCap = "round";
        canvasContext.strokeStyle = craftColor;
        
        canvasContext.beginPath();
        
        for (motorIndex = 0; motorIndex < numMotors; motorIndex++) {
            canvasContext.moveTo(0, 0);
    
            canvasContext.lineTo(
                (armLength * ARM_EXTEND_BEYOND_MOTOR_MULTIPLIER) * craftParameters.motors[motorIndex].x,
                (armLength * ARM_EXTEND_BEYOND_MOTOR_MULTIPLIER) * craftParameters.motors[motorIndex].y
            );
        }
    
        canvasContext.stroke();
    
        //Draw the central hub
        canvasContext.beginPath();
        
        canvasContext.moveTo(0, 0);
        canvasContext.arc(0, 0, armLength * CENTRAL_HUB_SIZE_MULTIPLIER, 0, 2 * Math.PI);
        
        canvasContext.fillStyle = craftColor;
        canvasContext.fill();
    
        for (motorIndex = 0; motorIndex < numMotors; motorIndex++) {
            var motorValue = frame[frameFieldIndexes["motor[" + motorIndex + "]"]];
            
            canvasContext.save();
            {
                //Move to the motor center
                canvasContext.translate(
                    armLength * craftParameters.motors[motorIndex].x,
                    armLength * craftParameters.motors[motorIndex].y
                );
    
                canvasContext.fillStyle = shadeColors[motorIndex];
    
                canvasContext.beginPath();
                
                canvasContext.moveTo(0, 0);
                canvasContext.arc(0, 0, bladeRadius, 0, Math.PI * 2, false);
                
                canvasContext.fill();
    
                canvasContext.fillStyle = propColors[motorIndex];
    
                canvasContext.beginPath();
    
                canvasContext.moveTo(0, 0);
                canvasContext.arc(0, 0, bladeRadius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 
                        * Math.max(motorValue - sysConfig.minthrottle, 0) / (sysConfig.maxthrottle - sysConfig.minthrottle), false);
                
                canvasContext.fill();
    
                var
                    motorLabel = "" + motorValue;
    
                if (craftParameters.motors[motorIndex].x > 0) {
                    canvasContext.textAlign = 'left';
                    canvasContext.fillText(motorLabel, bladeRadius + MOTOR_LABEL_SPACING, 0);
                } else {
                    canvasContext.textAlign = 'right';
                    canvasContext.fillText(motorLabel, -(bladeRadius + MOTOR_LABEL_SPACING), 0);
                }
    
            }
            canvasContext.restore();
        }
    };
    
    for (var i = 0; i < propColors.length; i++) {
        shadeColors.push(makeColorHalfStrength(propColors[i]));
    }
    
    this.resize = function(height) {
        armLength = 0.5 * height;
        
        if (numMotors >= 6) {
            bladeRadius = armLength * 0.4;
        } else {
            bladeRadius = armLength * 0.6;
        }
    };
    
    // Assume we're to fill the entire canvas until we're told otherwise by .resize()
    this.resize(canvas.height);
}