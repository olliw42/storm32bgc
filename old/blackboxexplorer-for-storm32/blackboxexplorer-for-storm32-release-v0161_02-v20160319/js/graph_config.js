"use strict";

function GraphConfig(graphConfig) {
    var
        graphs = graphConfig ? graphConfig : [],
        listeners = [],
        that = this;
    
    function notifyListeners() {
        for (var i = 0; i < listeners.length; i++) {
            listeners[i](that);
        }
    }
    
    this.getGraphs = function() {
        return graphs;
    };
    
    /**
     * newGraphs is an array of objects like {label: "graph label", height:, fields:[{name: curve:{offset:, power:, inputRange:, outputRange:, steps:}, color:, }, ...]}
     */
    this.setGraphs = function(newGraphs) {
        graphs = newGraphs;
        
        notifyListeners();
    };
    
    /**
     * Convert the given graph configs to make them appropriate for the given flight log.
     */
    this.adaptGraphs = function(flightLog, graphs) {
        var 
            logFieldNames = flightLog.getMainFieldNames(),
            
            // Make copies of graphs into here so we can modify them without wrecking caller's copy
            newGraphs = [];
        
        for (var i = 0; i < graphs.length; i++) {
            var 
                graph = graphs[i],
                newGraph = $.extend(
                    // Default values for missing properties:
                    {
                        height: 1
                    }, 
                    // The old graph
                    graph, 
                    // New fields to replace the old ones:
                    {
                        fields:[]
                    }
                ),
                colorIndex = 0;
            
            for (var j = 0; j < graph.fields.length; j++) {
                var
                    field = graph.fields[j],
                    matches,
                    defaultCurve;
                
                var adaptField = function(field) {
                    defaultCurve = GraphConfig.getDefaultCurveForField(flightLog, field.name);
                    
                    if (field.curve === undefined) {
                        field.curve = defaultCurve;
                    } else {
                        /* The curve may have been originally created for a craft with different endpoints, so use the 
                         * recommended offset and input range instead of the provided one.
                         */
                        field.curve.offset = defaultCurve.offset;
                        field.curve.inputRange = defaultCurve.inputRange;
                    }
                    
                    if (field.color === undefined) {
                        field.color = GraphConfig.PALETTE[colorIndex % GraphConfig.PALETTE.length];
                        colorIndex++;
                    }
                    
                    if (field.smoothing === undefined) {
                        field.smoothing = GraphConfig.getDefaultSmoothingForField(flightLog, field.name);
                    }
                    
                    return field;
                };
                
                if ((matches = field.name.match(/^(.+)\[all\]$/))) {
                    var 
                        nameRoot = matches[1],
                        nameRegex = new RegExp("^" + nameRoot + "\[[0-9]+\]$");
                    
                    for (var k = 0; k < logFieldNames.length; k++) {
                        if (logFieldNames[k].match(nameRegex)) {
                            newGraph.fields.push(adaptField($.extend({}, field, {name: logFieldNames[k]})));
                        }
                    }
                } else {
                    // Don't add fields if they don't exist in this log
                    if (flightLog.getMainFieldIndexByName(field.name) !== undefined) {
                        newGraph.fields.push(adaptField($.extend({}, field)));
                    }
                }
            }
            
            newGraphs.push(newGraph);
        }
        
        this.setGraphs(newGraphs);
    };
    
    this.addListener = function(listener) {
        listeners.push(listener);
    };
}

GraphConfig.PALETTE = [
    "#fb8072", // Red
    "#8dd3c7", // Cyan
    "#ffffb3", // Yellow
    "#bebada", // Purple
    "#80b1d3",
    "#fdb462",
    "#b3de69",
    "#fccde5",
    "#d9d9d9",
    "#bc80bd",
    "#ccebc5",
    "#ffed6f"
];

GraphConfig.load = function(config) {
    // Upgrade legacy configs to suit the newer standard by translating field names
    if (config) {
        for (var i = 0; i < config.length; i++) {
            var graph = config[i];
            
            for (var j = 0; j < graph.fields.length; j++) {
                var 
                    field = graph.fields[j],
                    matches;
                
                if ((matches = field.name.match(/^gyroData(.+)$/))) {
                    field.name = "gyroADC" + matches[1];
                }
            }
        }
    } else {
        config = false;
    }
    
    return config;
};

(function() {
    var
        EXAMPLE_GRAPHS = [
            {
                label: "Motors",
                fields: ["motor[all]", "servo[5]"]
            },
            {
                label: "Gyros",
                fields: ["gyroADC[all]"]
            },
            {
                label: "PIDs",
                fields: ["axisSum[all]"]
            },
            {
                label: "Gyro + PID roll",
                fields: ["axisP[0]", "axisI[0]", "axisD[0]", "gyroADC[0]"]
            },
            {
                label: "Gyro + PID pitch",
                fields: ["axisP[1]", "axisI[1]", "axisD[1]", "gyroADC[1]"]
            },
            {
                label: "Gyro + PID yaw",
                fields: ["axisP[2]", "axisI[2]", "axisD[2]", "gyroADC[2]"]
            },
            {
                label: "Accelerometers",
                fields: ["accSmooth[all]"]
            },
        ], //;
//ow ###################################            
        EXAMPLE_GRAPHS_STORM32 = [
            {
                label: "Perfomance",
                //fields: ["Imu1rx", "Imu1done", "PIDdone", "Motdone", "Imu2rx", "Imu2done", "Loopdone"]
                fields: ["Imu1rx", "Imu1done", "PIDdone", "Motdone", "Loopdone"]
            },
            {
                label: "Imu1",
                fields: ["Imu1[all]"]
            },
            {
                label: "Imu2",
                fields: ["Imu2[all]"]
            },
            {
                label: "PID",
                fields: ["PID[all]"]
            },
            {
                label: "PIDMot",
                fields: ["PIDMot[all]"]
            },
            {
                label: "Vibe1",
                fields: ["Vibe1[all]"]
            },
            {
                label: "Vibe2",
                fields: ["Vibe2[all]"]
            },
            {
                label: "Ahrs1",
                fields: ["AccAmp1", "AccConf1"]
            },
            {
                label: "a1 raw",
                fields: ["a1raw[all]"]
            },
            {
                label: "g1 raw",
                fields: ["g1raw[all]"]
            },
            {
                label: "a2 raw",
                fields: ["a2raw[all]"]
            },
            {
                label: "g2 raw",
                fields: ["g2raw[all]"]
            },
            {
                label: "a3 raw",
                fields: ["a3raw[all]"]
            },
            {
                label: "g3 raw",
                fields: ["g3raw[all]"]
            },
        ];
//ow -----------------------------------

    GraphConfig.getDefaultSmoothingForField = function(flightLog, fieldName) {
        if (fieldName.match(/^motor\[/)) {
            return 5000;
        } else if (fieldName.match(/^servo\[/)) {
            return 5000;
        } else if (fieldName.match(/^gyroADC\[/)) {
            return 3000;
        } else if (fieldName.match(/^accSmooth\[/)) {
            return 3000;
        } else if (fieldName.match(/^axis.+\[/)) {
            return 3000;
        } else {
            return 0;
        }
    };
    
    GraphConfig.getDefaultCurveForField = function(flightLog, fieldName) {
        var
            sysConfig = flightLog.getSysConfig();
        
        if (fieldName.match(/^motor\[/)) {
            return {
                offset: -(sysConfig.maxthrottle + sysConfig.minthrottle) / 2,
                power: 1.0,
                inputRange: (sysConfig.maxthrottle - sysConfig.minthrottle) / 2,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^servo\[/)) {
            return {
                offset: -1500,
                power: 1.0,
                inputRange: 500,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^gyroADC\[/)) {
            return {
                offset: 0,
                power: 0.25,
                inputRange: 2.0e-5 / sysConfig.gyroScale,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^accSmooth\[/)) {
            return {
                offset: 0,
                power: 0.5,
                inputRange: sysConfig.acc_1G * 3.0, /* Reasonable typical maximum for acc */
                outputRange: 1.0
            };
        } else if (fieldName.match(/^axis.+\[/)) {
            return {
                offset: 0,
                power: 0.3,
                inputRange: 400,
                outputRange: 1.0
            };
        } else if (fieldName == "rcCommand[3]") { // Throttle
            return {
                offset: -1500,
                power: 1.0,
                inputRange: 500,
                outputRange: 1.0
            };
        } else if (fieldName == "rcCommand[2]") { // Yaw
            return {
                offset: 0,
                power: 0.8,
                inputRange: 500,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^rcCommand\[/)) {
            return {
                offset: 0,
                power: 0.8,
                inputRange: 500 * (sysConfig.rcRate ? sysConfig.rcRate : 100) / 100,
                outputRange: 1.0
            };
        } else if (fieldName == "heading[2]") {
            return {
                offset: -Math.PI,
                power: 1.0,
                inputRange: Math.PI,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^heading\[/)) {
            return {
                offset: 0,
                power: 1.0,
                inputRange: Math.PI,
                outputRange: 1.0
            };
        } else if (fieldName.match(/^sonar.*/)) {
            return {
                offset: -200,
                power: 1.0,
                inputRange: 200,
                outputRange: 1.0
            };
//ow ###################################
        } else if (sysConfig.firmwareType == gFIRMWARE_TYPE_STORM32) {    
            var //could come later, but gives one indent less
                stats = flightLog.getStats(),
                fieldIndex = flightLog.getMainFieldIndexByName(fieldName),
                fieldStat = fieldIndex !== undefined ? stats.field[fieldIndex] : false;

            if (fieldName.match(/.*?done$/) || fieldName.match(/.*?rx$/)) {
                return {
                    offset: -1500 / 2,
                    power: 1.0,
                    inputRange: 1.2* 1500 / 2,
                    outputRange: 1.0
                };
            } else if (fieldStat) {
                return {
                    offset: -(fieldStat.max + fieldStat.min) / 2,
                    power: 1.0,
                    inputRange: Math.max(1.2*(fieldStat.max - fieldStat.min) / 2, 1.0),
                    outputRange: 1.0
                };
            } else {
                return { 
                    offset: 0, 
                    power: 1.0, 
                    inputRange: 500, 
                    outputRange: 1.0 
                };
            }
//ow -----------------------------------
        } else {
            // Scale and center the field based on the whole-log observed ranges for that field
            var
                stats = flightLog.getStats(),
                fieldIndex = flightLog.getMainFieldIndexByName(fieldName),
                fieldStat = fieldIndex !== undefined ? stats.field[fieldIndex] : false;
            
            if (fieldStat) {
                return {
                    offset: -(fieldStat.max + fieldStat.min) / 2,
                    power: 1.0,
                    inputRange: Math.max(1.2*(fieldStat.max - fieldStat.min) / 2, 1.0),
                    outputRange: 1.0
                };
            } else {
                return {
                    offset: 0,
                    power: 1.0,
                    inputRange: 500,
                    outputRange: 1.0
                };
            }
        }
    };
    
    /**
     * Get an array of suggested graph configurations will be usable for the fields available in the given flightlog.
     * 
     * Supply an array of strings `graphNames` to only fetch the graph with the given names.
     */
    GraphConfig.getExampleGraphConfigs = function(flightLog, graphNames) {
        var
//ow ###################################
            sysConfig = flightLog.getSysConfig(),
            exampleGraphs,
//ow -----------------------------------
            result = [],
            i, j;
        
//ow ###################################
        if (sysConfig.firmwareType != gFIRMWARE_TYPE_STORM32) {
            exampleGraphs = EXAMPLE_GRAPHS;  //is this a copy or a reference??? reference would be prefered / I think it's a reference
        } else {
            exampleGraphs = EXAMPLE_GRAPHS_STORM32;
        }
//ow -----------------------------------

//ow ###################################
//        for (i = 0; i < EXAMPLE_GRAPHS.length; i++) {
        for (i = 0; i < exampleGraphs.length; i++) {
//ow -----------------------------------
            var
//ow ###################################
//                srcGraph = EXAMPLE_GRAPHS[i],
                srcGraph = exampleGraphs[i],
//ow -----------------------------------
                destGraph = {
                    label: srcGraph.label, 
                    fields: [],
                    height: srcGraph.height || 1
                },
                found;
            
            if (graphNames !== undefined) {
                found = false;
                for (j = 0; j < graphNames.length; j++) {
                    if (srcGraph.label == graphNames[j]) {
                        found = true;
                        break;
                    }
                }
                
                if (!found) {
                    continue;
                }
            }
            
            for (j = 0; j < srcGraph.fields.length; j++) {
                var 
                    srcFieldName = srcGraph.fields[j],
                    destField = {
                        name: srcFieldName, 
                    };
                
                destGraph.fields.push(destField);
            }
            
            result.push(destGraph);
        }
        
        return result;
    };
})();
