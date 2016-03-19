"use strict";

/**
 * Creates a lookup-table based expo curve, which takes values that range between -inputrange and +inputRange, and
 * scales them to -outputRange to +outputRange with the given power curve (curve <1.0 exaggerates values near the origin,
 * curve = 1.0 is a straight line mapping). 
 */
function ExpoCurve(offset, power, inputRange, outputRange, steps) {
    var
        curve, inputScale;
    
    function lookupStraightLine(input) {
        return (input + offset) * inputScale;
    }

    /**
     * An approximation of lookupMathPow by precomputing several expo curve points and interpolating between those
     * points using straight line interpolation.
     * 
     * The error will be largest in the area of the curve where the slope changes the fastest with respect to input
     * (e.g. the approximation will be too straight near the origin when power < 1.0, but a good fit far from the origin)
     */
    function lookupInterpolatedCurve(input) {
        var
            valueInCurve,
            prevStepIndex;

        input += offset;

        valueInCurve = Math.abs(input * inputScale);
        prevStepIndex = Math.floor(valueInCurve);

        /* If the input value lies beyond the stated input range, use the final
         * two points of the curve to extrapolate out (the "curve" out there is a straight line, though)
         */
        if (prevStepIndex > steps - 2) {
            prevStepIndex = steps - 2;
        }

        //Straight-line interpolation between the two curve points
        var 
            proportion = valueInCurve - prevStepIndex,
            result = curve[prevStepIndex] + (curve[prevStepIndex + 1] - curve[prevStepIndex]) * proportion;

        if (input < 0)
            return -result;
        return result;
    }
    
    function lookupMathPow(input) {
        input += offset;
        
        var 
            result = Math.pow(Math.abs(input) / inputRange, power) * outputRange;
        
        if (input < 0)
            return -result;
        return result;
    }
    
    // If steps argument isn't supplied, use a reasonable default
    if (steps === undefined) {
        steps = 12;
    }
    
    if (steps <= 2 || power == 1.0) {
        //Curve is actually a straight line
        inputScale = outputRange / inputRange;
        
        this.lookup = lookupStraightLine;
    } else {
        var 
            stepSize = 1.0 / (steps - 1),
            i;

        curve = new Array(steps);
    
        inputScale = (steps - 1) / inputRange;

        for (i = 0; i < steps; i++) {
            curve[i] = Math.pow(i * stepSize, power) * outputRange;
        }
        
        this.lookup = lookupInterpolatedCurve;
    }
}
