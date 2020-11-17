"use strict";

function FlightLogIndex(logData) {
    //Private:
    var 
        that = this,
        logBeginOffsets = false,
        logCount = false,
        intraframeDirectories = false;
        
    function buildLogOffsetsIndex() {
        var 
            stream = new ArrayDataStream(logData), 
            i, logStart;
        
        logBeginOffsets = [];
    
        for (i = 0; ; i++) {
            logStart = stream.nextOffsetOf(FlightLogParser.prototype.FLIGHT_LOG_START_MARKER);
    
            if (logStart == -1) {
                //No more logs found in the file
                logBeginOffsets.push(stream.end);
                break; 
            }
    
            logBeginOffsets.push(logStart);
            
            //Restart the search after this header
            stream.pos = logStart + FlightLogParser.prototype.FLIGHT_LOG_START_MARKER.length;
        }
    }
    
    function buildIntraframeDirectories() {
        var 
            parser = new FlightLogParser(logData, that);
        
        intraframeDirectories = [];

        for (var i = 0; i < that.getLogCount(); i++) {
            var 
                intraIndex = {
                    times: [],
                    offsets: [],
                    avgThrottle: [],
                    initialIMU: [],
                    initialSlow: [],
                    initialGPSHome: [],
                    hasEvent: [],
                    minTime: false,
                    maxTime: false
                },
                
                imu = new IMU(),
                gyroADC, accSmooth, magADC,
                
                iframeCount = 0,
                motorFields = [],
                matches,
                throttleTotal,
                eventInThisChunk = null,
                parsedHeader,
                sawEndMarker = false;
            
            try {
                parser.parseHeader(logBeginOffsets[i], logBeginOffsets[i + 1]);
                parsedHeader = true;
            } catch (e) {
                console.log("Error parsing header of log #" + (i + 1) + ": " + e);
                intraIndex.error = e;
                
                parsedHeader = false;
            }

            // Only attempt to parse the log if the header wasn't corrupt
            if (parsedHeader) {
                var 
                    sysConfig = parser.sysConfig,
                    mainFrameDef = parser.frameDefs.I,
                    
                    gyroADC = [mainFrameDef.nameToIndex["gyroADC[0]"], mainFrameDef.nameToIndex["gyroADC[1]"], mainFrameDef.nameToIndex["gyroADC[2]"]],
                    accSmooth = [mainFrameDef.nameToIndex["accSmooth[0]"], mainFrameDef.nameToIndex["accSmooth[1]"], mainFrameDef.nameToIndex["accSmooth[2]"]],
                    magADC = [mainFrameDef.nameToIndex["magADC[0]"], mainFrameDef.nameToIndex["magADC[1]"], mainFrameDef.nameToIndex["magADC[2]"]],
                    
//ow ###################################
                    storm32State = mainFrameDef.nameToIndex["State"],
                    storm32Voltage = mainFrameDef.nameToIndex["Voltage"],
//ow -----------------------------------
                    
                    lastSlow = [],
                    lastGPSHome = [];
                
                // Identify motor fields so they can be used to show the activity summary bar
                for (var j = 0; j < 8; j++) {
                    if (mainFrameDef.nameToIndex["motor[" + j + "]"] !== undefined) {
                        motorFields.push(mainFrameDef.nameToIndex["motor[" + j + "]"]);
                    }
                }
                
                // Do we have mag fields? If not mark that data as absent
                if (magADC[0] === undefined) {
                    magADC = false;
                }
                
                parser.onFrameReady = function(frameValid, frame, frameType, frameOffset, frameSize) {
                    if (!frameValid) {
                        return;
                    }
                    
                    switch (frameType) {
                        case 'P':
                        case 'I':
                            var 
                                frameTime = frame[FlightLogParser.prototype.FLIGHT_LOG_FIELD_INDEX_TIME];
                            
                            if (intraIndex.minTime === false) {
                                intraIndex.minTime = frameTime;
                            }
                            
                            if (intraIndex.maxTime === false || frameTime > intraIndex.maxTime) {
                                intraIndex.maxTime = frameTime;
                            }
                            
                            if (frameType == 'I') {
                                // Start a new chunk on every 4th I-frame
                                if (iframeCount % 4 === 0) {
                                    // Log the beginning of the new chunk
                                    intraIndex.times.push(frameTime);
                                    intraIndex.offsets.push(frameOffset);
                                    
                                    if (motorFields.length) {
                                        throttleTotal = 0;
                                        for (var j = 0; j < motorFields.length; j++) {
                                            throttleTotal += frame[motorFields[j]];
                                        }
                                        
                                        intraIndex.avgThrottle.push(Math.round(throttleTotal / motorFields.length));
                                    }
                                    
//ow ###################################
                                    if (sysConfig.firmwareType == gFIRMWARE_TYPE_STORM32){
                                        if (frame[storm32State] == 6 && frame[storm32Voltage] > 5500) {
                                            intraIndex.avgThrottle.push(2000); 
                                        } else if (frame[storm32State] == 6) { 
                                            intraIndex.avgThrottle.push(1500); 
                                        } else {
                                            intraIndex.avgThrottle.push(1000); 
                                        }
                                    }
//ow -----------------------------------
                                    
                                    /* To enable seeking to an arbitrary point in the log without re-reading anything
                                     * that came before, we have to record the initial state of various items which aren't
                                     * logged anew every iteration.
                                     */ 
                                    intraIndex.initialIMU.push(new IMU(imu));
                                    intraIndex.initialSlow.push(lastSlow);
                                    intraIndex.initialGPSHome.push(lastGPSHome);
                                }
                                
                                iframeCount++;
                            }
                            
                            imu.updateEstimatedAttitude(
                                [frame[gyroADC[0]], frame[gyroADC[1]], frame[gyroADC[2]]],
                                [frame[accSmooth[0]], frame[accSmooth[1]], frame[accSmooth[2]]],
                                frame[FlightLogParser.prototype.FLIGHT_LOG_FIELD_INDEX_TIME], 
                                sysConfig.acc_1G, 
                                sysConfig.gyroScale, 
                                magADC ? [frame[magADC[0]], frame[magADC[1]], frame[magADC[2]]] : false
                            );
                        break;
                        case 'H':
                            lastGPSHome = frame.slice(0);
                        break;
                        case 'E':
                            // Mark that there was an event inside the current chunk
                            if (intraIndex.times.length > 0) {
                                intraIndex.hasEvent[intraIndex.times.length - 1] = true;
                            }
                            
                            if (frame.event == FlightLogEvent.LOG_END) {
                                sawEndMarker = true;
                            }
                        break;
                        case 'S':
                            lastSlow = frame.slice(0);
                        break;
                    }
                };
            
                try {
                    parser.parseLogData(false);
                } catch (e) {
                    intraIndex.error = e;
                }
                
                // Don't bother including the initial (empty) states for S and H frames if we didn't have any in the source data
                if (!parser.frameDefs.S) {
                    delete intraIndex.initialSlow;
                }

                if (!parser.frameDefs.H) {
                    delete intraIndex.initialGPSHome;
                }

                intraIndex.stats = parser.stats;
            }
            
            // Did we not find any events in this log?
            if (intraIndex.minTime === false) {
                if (sawEndMarker) {
                    intraIndex.error = "Logging was paused, no data recorded";
                } else {
                    intraIndex.error = "Log is truncated, contains no data";
                }
            }
        
            intraframeDirectories.push(intraIndex);
        }
    }
    
    //Public: 
    this.loadFromJSON = function(json) {
        
    };
    
    this.saveToJSON = function() {
        var 
            intraframeDirectories = this.getIntraframeDirectories(),
            i, j, 
            resultIndexes = new Array(intraframeDirectories.length);
        
        for (i = 0; i < intraframeDirectories.length; i++) {
            var 
                lastTime, lastLastTime, 
                lastOffset, lastLastOffset,
                lastThrottle,
                
                sourceIndex = intraframeDirectories[i],
                
                resultIndex = {
                    times: new Array(sourceIndex.times.length), 
                    offsets: new Array(sourceIndex.offsets.length),
                    minTime: sourceIndex.minTime,
                    maxTime: sourceIndex.maxTime,
                    avgThrottle: new Array(sourceIndex.avgThrottle.length)
                };
            
            if (sourceIndex.times.length > 0) {
                resultIndex.times[0] = sourceIndex.times[0];
                resultIndex.offsets[0] = sourceIndex.offsets[0];
                
                lastLastTime = lastTime = sourceIndex.times[0];
                lastLastOffset = lastOffset = sourceIndex.offsets[0];
                
                for (j = 1; j < sourceIndex.times.length; j++) {
                    resultIndex.times[j] = sourceIndex.times[j] - 2 * lastTime + lastLastTime;
                    resultIndex.offsets[j] = sourceIndex.offsets[j] - 2 * lastOffset + lastLastOffset;
                    
                    lastLastTime = lastTime;
                    lastTime = sourceIndex.times[j];
    
                    lastLastOffset = lastOffset;
                    lastOffset = sourceIndex.offsets[j];
                }
            }
            
            if (sourceIndex.avgThrottle.length > 0) {
                for (j = 0; j < sourceIndex.avgThrottle.length; j++) {
                    resultIndex.avgThrottle[j] = sourceIndex.avgThrottle[j] - 1000;
                }
            }
            
            resultIndexes[i] = resultIndex;
        }
        
        return JSON.stringify(resultIndexes);
    };  
    
    this.getLogBeginOffset = function(index) {
        if (!logBeginOffsets)
            buildLogOffsetsIndex();
        
        return logBeginOffsets[index];
    };
    
    this.getLogCount = function() {
        if (!logBeginOffsets)
            buildLogOffsetsIndex();

        return logBeginOffsets.length - 1;
    };
    
    this.getIntraframeDirectories = function() {
        if (!intraframeDirectories)
            buildIntraframeDirectories();
        
        return intraframeDirectories;
    };
    
    this.getIntraframeDirectory = function(logIndex) {
        return this.getIntraframeDirectories()[logIndex];
    };
}
