"use strict";

function assert(condition) {
    if (!condition) {
        throw "Assert failed";
    }
}

function testExpoCurve() {
    var 
        curve = new ExpoCurve(0, 0.700, 750, 1.0, 10);

    assert(curve.lookup(0) == 0.0);
    assert(curve.lookup(-750) == -1.0);
    assert(curve.lookup(750) == 1.0);
}

function testExpoStraightLine() {
    var 
        curve = new ExpoCurve(0, 1.0, 500, 1.0, 1);
    
    assert(curve.lookup(0) == 0.0);
    assert(curve.lookup(-500) == -1.0);
    assert(curve.lookup(500) == 1.0);
    assert(curve.lookup(-250) == -0.5);
    assert(curve.lookup(250) == 0.5);
}

function benchExpoCurve() {
    var 
        trial, i,
        curve = new ExpoCurve(0, 0.700, 750, 1.0, 10),
        acc = 0,
        endTime, results = "";
    
    for (trial = 0; trial < 10; trial++) {
        var 
            start = Date.now(),
            end;
        
        for (i = 0; i < 10000000; i++) {
            acc += curve.lookup(Math.random() * 750); 
        }
        
        end = Date.now();
        
        results += (end - start) + "\n";
    }
    
    alert("Expo curve bench\n" + results);
}

try {
    testExpoCurve();
    testExpoStraightLine();
    
    //benchExpoCurve();
    
    alert("All tests pass");
} catch (e) {
    alert(e);
}