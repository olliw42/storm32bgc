"use strict";

function FlightLogGrapher(flightLog, graphConfig, canvas, craftCanvas, options) {
    var
        PID_P = 0,
        PID_I = 1,
        PID_D = 2,
        
        WHITE = "white",
        
        DEFAULT_FONT_FACE = "Verdana, Arial, sans-serif",
        
        drawingParams = {
            fontSizeCurrentValueLabel: null,
            fontSizeCommandStickLabel: null,
            fontSizePIDTableLabel: null,
            fontSizeAxisLabel: null,
            fontSizeFrameLabel: null,
            fontSizeEventLabel: null,
            
            plotLineWidth: null,
            
            stickSpacing: null,
            commandStickLabelMargin: null,
        },
        
        // How far the center of the craft and command sticks are from the top of the canvas, as a portion of height
        COMMAND_STICK_POSITION_Y_PROPORTION = 0.20,
        CRAFT_POSITION_Y_PROPORTION = 0.25,
        
        lineColors = [
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
        ],
        
        WINDOW_WIDTH_MICROS_DEFAULT = 1000000;

    var
        windowStartTime, windowCenterTime, windowEndTime,
        
        canvasContext = canvas.getContext("2d"),
        
        defaultOptions = {
            gapless:false,
            drawCraft:"3D", drawPidTable:true, drawSticks:true, drawTime:true,
            eraseBackground: true // Set to false if you want the graph to draw on top of an existing canvas image
        },
        
        windowWidthMicros = WINDOW_WIDTH_MICROS_DEFAULT,
        
        idents,
        
        sysConfig = flightLog.getSysConfig(),

        graphs = [],
        pitchStickCurve = new ExpoCurve(0, 0.700, 500 * (sysConfig.rcRate ? sysConfig.rcRate : 100) / 100, 1.0, 10),

        inTime = false, outTime = false,
        
        lastMouseX, lastMouseY,
        
        craft3D = null, craft2D = null,
        
        that = this;
    
    this.onSeek = null;
    
    function extend(base, top) {
        var 
            target = {};
        
        [base, top].forEach(function(obj) {
            for (var prop in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, prop)) {
                    target[prop] = obj[prop];
                }
            }
        });
        
        return target;
    }
    
    function onMouseMove(e) {
        e.preventDefault();
        
        if (that.onSeek) {
            //Reverse the seek direction so that it looks like you're dragging the data with the mouse
            that.onSeek((lastMouseX - e.pageX) / canvas.width * windowWidthMicros); 
        }
        
        lastMouseX = e.pageX;
        lastMouseY = e.pageY;
    }
    
    function onMouseDown(e) {
        if (e.which == 1) { //Left mouse button only for seeking
            lastMouseX = e.pageX;
            lastMouseY = e.pageY;
            
            //"capture" the mouse so we can drag outside the boundaries of canvas
            $(document).on("mousemove", onMouseMove);
            
            //Release the capture when the mouse is released
            $(document).one("mouseup", function () {
                $(document).off("mousemove", onMouseMove);
            });
            
            e.preventDefault();
        }
    }
    
    function identifyFields() {
        var 
            motorGraphColorIndex = 0,
            fieldIndex,
            fieldNames = flightLog.getMainFieldNames();
        
        idents = {
            rcCommandFields:[],
            motorFields:[],
            motorColors:[],

            axisPIDFields: [[], [], []],  //First dimension is [P, I, D], second dimension is axis

            gyroFields:[],

            accFields:[],

            servoFields:[],

            vbatField:-1,
            numCells:-1,
            baroField:-1,

            miscFields:[],

            //Synthetic fields:
            roll:-1,
            pitch:-1,
            heading:-1,
            axisPIDSum:[]
        };
        
        for (fieldIndex = 0; fieldIndex < fieldNames.length; fieldIndex++) {
            var 
                fieldName = fieldNames[fieldIndex],
                matches;

            if ((matches = fieldName.match(/^motor\[(\d+)]$/))) {
                var motorIndex = matches[1];

                idents.motorFields[motorIndex] = fieldIndex;
                idents.motorColors[motorIndex] = lineColors[(motorGraphColorIndex++) % lineColors.length];
            } else if ((matches = fieldName.match(/^rcCommand\[(\d+)]$/))) {
                var rcCommandIndex = matches[1];

                if (rcCommandIndex >= 0 && rcCommandIndex < 4) {
                    idents.rcCommandFields[rcCommandIndex] = fieldIndex;
                }
            } else if ((matches = fieldName.match(/^axisPID\[(\d+)]$/))) {
                var axisIndex = matches[1];

                idents.axisPIDSum[axisIndex] = fieldIndex;
            } else if ((matches = fieldName.match(/^axis(.)\[(\d+)]$/))) {
                var axisIndex = matches[2];
                
                idents.axisPIDFields[matches[1]] = axisIndex;
                idents.hasPIDs = true;
            } else if ((matches = fieldName.match(/^gyroADC\[(\d+)]$/))) {
                var axisIndex = matches[1];

                idents.gyroFields[axisIndex] = fieldIndex;
            } else if ((matches = fieldName.match(/^accSmooth\[(\d+)]$/))) {
                var axisIndex = matches[1];

                idents.accFields[axisIndex] = fieldIndex;
            } else if ((matches = fieldName.match(/^servo\[(\d+)]$/))) {
                var servoIndex = matches[1];

                idents.numServos++;
                idents.servoFields[servoIndex] = fieldIndex;
            } else {
                switch (fieldName) {
                    case "vbatLatest":
                        idents.vbatField = fieldIndex;
                        idents.numCells = flightLog.getNumCellsEstimate();
                    break;
                    case "BaroAlt":
                        idents.baroField = fieldIndex;
                    break;
                    case "roll":
                        idents.roll = fieldIndex;
                    break;
                    case "pitch":
                        idents.pitch = fieldIndex;
                    break;
                    case "heading":
                        idents.heading = fieldIndex;
                    break;
                    default:
                        idents.miscFields.push(fieldIndex);
                }
            }
        }
    }
    
    /**
     * Examine the log metadata to determine the layout of motors for the 2D craft model. Returns the craft parameters
     * object.
     */
    function decide2DCraftParameters() {
        var
            craftParameters = {};
        
        switch (idents.motorFields.length) {
            case 3:
                craftParameters.motors = [
                    {
                        x: 0,
                        y: 1,
                        direction: -1,
                        color: idents.motorColors[0]
                    }, {
                        x: 0.71,
                        y: -0.71,
                        direction: -1,
                        color: idents.motorColors[1]
                    }, {
                        x: -0.71,
                        y: -0.71,
                        direction: -1,
                        color: idents.motorColors[2]
                    }
                ];
            break;
            case 4:
                craftParameters.motors = [
                    {
                        x: 0.71,
                        y: 0.71,
                        direction: 1,
                        color: idents.motorColors[0]
                    }, {
                        x: 0.71,
                        y: -0.71,
                        direction: -1,
                        color: idents.motorColors[1]
                    }, {
                        x: -0.71,
                        y: 0.71,
                        direction: -1,
                        color: idents.motorColors[2]
                    }, {
                        x: -0.71,
                        y: -0.71,
                        direction: 1,
                        color: idents.motorColors[3]
                    }
                ];
            break;
            default:
                craftParameters.motors = [];
            
                for (var i = 0; i < idents.motorFields.length; i++) {
                    craftParameters.motors.push({
                        x: Math.cos(i / idents.motorFields.length * Math.PI * 2),
                        y: Math.sin(i / idents.motorFields.length * Math.PI * 2),
                        direction: Math.pow(-1, i),
                        color: idents.motorColors[i]
                    });
                }
            break;
        }
        
        return craftParameters;
    }
    
    function drawCommandSticks(frame) {
        var
            // The total width available to draw both sticks in:
            sticksDisplayWidth = canvas.width * 0.3,
            
            // Use that plus the inter-stick spacing that has been determined already to decide how big each stick should be:
            stickSurroundRadius = Math.min((sticksDisplayWidth - drawingParams.stickSpacing) / 4, canvas.height / 10), 
            yawStickMax = 500,
            
            stickColor = "rgba(255,102,102,1.0)",
            stickAreaColor = "rgba(76,76,76,0.8)",
            crosshairColor = "rgba(191,191,191,0.5)";
        
        var
            stickIndex,
            rcCommand = [],
            stickPositions = [],
            stickLabel;

        for (stickIndex = 0; stickIndex < 4; stickIndex++) {
            //Check that stick data is present to be drawn:
            if (idents.rcCommandFields[stickIndex] === undefined)
                return;

            rcCommand[stickIndex] = frame[idents.rcCommandFields[stickIndex]];
        }

        //Compute the position of the sticks in the range [-1..1] (left stick x, left stick y, right stick x, right stick y)
        stickPositions[0] = -rcCommand[2] / yawStickMax; //Yaw
        stickPositions[1] = (1500 - rcCommand[3]) / 500; //Throttle
        stickPositions[2] = pitchStickCurve.lookup(rcCommand[0]); //Roll
        stickPositions[3] = pitchStickCurve.lookup(-rcCommand[1]); //Pitch

        for (stickIndex = 0; stickIndex < 4; stickIndex++) {
            //Clamp to [-1..1]
            stickPositions[stickIndex] = stickPositions[stickIndex] > 1 ? 1 : (stickPositions[stickIndex] < -1 ? -1 : stickPositions[stickIndex]);

            //Scale to our stick size
            stickPositions[stickIndex] *= stickSurroundRadius;
        }

        // Move origin to center of left stick
        canvasContext.translate(-drawingParams.stickSpacing / 2 - stickSurroundRadius, 0);

        canvasContext.font = drawingParams.fontSizeCommandStickLabel + "pt " + DEFAULT_FONT_FACE;

        //For each stick
        for (var i = 0; i < 2; i++) {
            //Fill in background
            canvasContext.beginPath();
            canvasContext.fillStyle = stickAreaColor;
            canvasContext.rect(-stickSurroundRadius, -stickSurroundRadius, stickSurroundRadius * 2, stickSurroundRadius * 2);
            canvasContext.fill();

            //Draw crosshair
            canvasContext.beginPath();
            canvasContext.lineWidth = 1;
            canvasContext.strokeStyle = crosshairColor;
            
            canvasContext.moveTo(-stickSurroundRadius, 0);
            canvasContext.lineTo(stickSurroundRadius, 0);
            
            canvasContext.moveTo(0, -stickSurroundRadius);
            canvasContext.lineTo(0, stickSurroundRadius);
            
            canvasContext.stroke();

            //Draw circle to represent stick position
            canvasContext.beginPath();
            canvasContext.fillStyle = stickColor;
            canvasContext.arc(stickPositions[i * 2 + 0], stickPositions[i * 2 + 1], stickSurroundRadius / 5, 0, 2 * Math.PI);
            canvasContext.fill();

            if (drawingParams.fontSizeCommandStickLabel) {
                canvasContext.fillStyle = WHITE;
                
                //Draw horizontal stick label
                stickLabel = frame[idents.rcCommandFields[(1 - i) * 2 + 0]] + "";
    
                canvasContext.textAlign = 'center';
                canvasContext.fillText(stickLabel, 0, stickSurroundRadius + drawingParams.fontSizeCurrentValueLabel + drawingParams.commandStickLabelMargin);
    
                //Draw vertical stick label
                stickLabel = frame[idents.rcCommandFields[(1 - i) * 2 + 1]] + "";
                
                canvasContext.textAlign = 'right';
                canvasContext.fillText(stickLabel, -stickSurroundRadius - drawingParams.commandStickLabelMargin, drawingParams.fontSizeCurrentValueLabel / 2);
            }
            
            //Advance to next stick
            canvasContext.translate(stickSurroundRadius + drawingParams.stickSpacing + stickSurroundRadius, 0);
        }
    }
    
    var
        frameLabelTextWidthFrameNumber,
        frameLabelTextWidthFrameTime;
    
    function drawFrameLabel(frameIndex, timeMsec)
    {
        var 
            extentFrameNumber, extentFrameTime;

        canvasContext.font = drawingParams.fontSizeFrameLabel + "pt " + DEFAULT_FONT_FACE;
        canvasContext.fillStyle = "rgba(255,255,255,0.65)";

        if (frameLabelTextWidthFrameNumber === undefined)
            frameLabelTextWidthFrameNumber = canvasContext.measureText("#0000000").width;
        
        canvasContext.fillText("#" + leftPad(frameIndex, "0", 7), canvas.width - frameLabelTextWidthFrameNumber - 8, canvas.height - 8);

        if (frameLabelTextWidthFrameTime === undefined)
            frameLabelTextWidthFrameTime = canvasContext.measureText("00:00.000").width;
        
        canvasContext.fillText(formatTime(timeMsec, true), canvas.width - frameLabelTextWidthFrameTime - 8, canvas.height - 8 - drawingParams.fontSizeFrameLabel - 8);
    }
    
    /**
     * Plot the given field within the specified time period. When the output from the curve applied to a field
     * value reaches 1.0 it'll be drawn plotHeight pixels away from the origin.
     */
    function plotField(chunks, startFrameIndex, fieldIndex, curve, plotHeight, color) {
        var
            GAP_WARNING_BOX_RADIUS = 3,
            chunkIndex, frameIndex,
            drawingLine = false,
            inGap = false,
            lastX, lastY,
            yScale = -plotHeight,
            xScale = canvas.width / windowWidthMicros;

        //Draw points from this line until we leave the window
        
        //We may start partway through the first chunk:
        frameIndex = startFrameIndex;
        
        canvasContext.strokeStyle = color;
        canvasContext.lineWidth = drawingParams.plotLineWidth;
        
        canvasContext.beginPath();
        
        plottingLoop:
        for (chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
            var 
                chunk = chunks[chunkIndex];
            
            for (; frameIndex < chunk.frames.length; frameIndex++) {
                var
                    fieldValue = chunk.frames[frameIndex][fieldIndex],
                    frameTime = chunk.frames[frameIndex][FlightLogParser.prototype.FLIGHT_LOG_FIELD_INDEX_TIME],
                    nextX, nextY;
    
                nextY = curve.lookup(fieldValue) * yScale;
                nextX = (frameTime - windowStartTime) * xScale;
    
                if (drawingLine) {
                    canvasContext.lineTo(nextX, nextY);

                    if (!options.gapless && chunk.gapStartsHere[frameIndex]) {
                        canvasContext.strokeRect(nextX - GAP_WARNING_BOX_RADIUS, nextY - GAP_WARNING_BOX_RADIUS, GAP_WARNING_BOX_RADIUS * 2, GAP_WARNING_BOX_RADIUS * 2);
                        inGap = true;
                        drawingLine = false;
                        continue;
                    } 
                } else {
                    canvasContext.moveTo(nextX, nextY);
                    
                    if (!options.gapless) {
                        // Is this the end of a gap to be marked?
                        if (inGap) {
                            canvasContext.strokeRect(nextX - GAP_WARNING_BOX_RADIUS, nextY - GAP_WARNING_BOX_RADIUS, GAP_WARNING_BOX_RADIUS * 2, GAP_WARNING_BOX_RADIUS * 2);
                            
                            if (chunk.gapStartsHere[frameIndex])
                                continue;
                            else
                                inGap = false;
                        } else if (chunk.gapStartsHere[frameIndex]) {
                            //Must be right at the beginning of drawing
                            inGap = true;
                            continue;
                        }
                    }
                }

                drawingLine = true;
                
                if (frameTime >= windowEndTime)
                    break plottingLoop;
            }
            
            frameIndex = 0;
        }

        canvasContext.stroke();
    }
    
    //Draw an origin line for a graph (at the origin and spanning the window)
    function drawAxisLine() {
        canvasContext.strokeStyle = "rgba(255,255,255,0.5)";
        canvasContext.lineWidth = 1;
        
        canvasContext.beginPath();
        canvasContext.moveTo(0, 0);
        canvasContext.lineTo(canvas.width, 0);
        
        canvasContext.stroke();
    }

    function drawAxisLabel(axisLabel) {
        canvasContext.font = drawingParams.fontSizeAxisLabel + "pt " + DEFAULT_FONT_FACE;
        canvasContext.fillStyle = "rgba(255,255,255,0.9)";
        canvasContext.textAlign = 'right';
        
        canvasContext.fillText(axisLabel, canvas.width - 8, -8);
    }
    
    function drawEventLine(x, labelY, label, color, width, labelColor) {
        width = width || 1.0;
        
        canvasContext.lineWidth = width;
        canvasContext.strokeStyle = color || "rgba(255,255,255,0.5)";
        
        canvasContext.beginPath();
        
        canvasContext.moveTo(x, 0);
        canvasContext.lineTo(x, canvas.height);
        
        canvasContext.stroke();
        
        if (label) {
            var 
                margin = 8,
                labelWidth = canvasContext.measureText(label).width + 2 * margin;
            
            canvasContext.lineWidth = 1;
            canvasContext.beginPath();
            canvasContext.moveTo(x + width - 1, labelY - drawingParams.fontSizeEventLabel/2);
            canvasContext.lineTo(x + margin, labelY - drawingParams.fontSizeEventLabel*1.5);
            canvasContext.lineTo(x + labelWidth, labelY - drawingParams.fontSizeEventLabel*1.5);
            canvasContext.lineTo(x + labelWidth, labelY + drawingParams.fontSizeEventLabel/2);
            canvasContext.lineTo(x + margin, labelY + drawingParams.fontSizeEventLabel/2);
            canvasContext.lineTo(x + width - 1, labelY - drawingParams.fontSizeEventLabel/2);
            canvasContext.fillStyle = color || "rgba(255,255,255,0.5)";
            canvasContext.fill();
            canvasContext.stroke();
            canvasContext.fillStyle = labelColor || "rgba(200,200,200,0.9)";
            canvasContext.closePath();
            canvasContext.fillText(label, x + width + 8, labelY);
          
        }
    }
    
    function timeToCanvasX(time) {
        return canvas.width / windowWidthMicros * (time - windowStartTime);
    }
    
    function drawEvent(event, sequenceNum) {
        var 
            x = timeToCanvasX(event.time),
            labelY = (sequenceNum + 1) * (drawingParams.fontSizeEventLabel + 10);
        
        switch (event.event) {
            case FlightLogEvent.AUTOTUNE_TARGETS:
                canvasContext.beginPath();

                canvasContext.moveTo(x, canvas.height / 2 - 25);
                canvasContext.lineTo(x, canvas.height / 2 + 25);
                
                canvasContext.stroke();
            break;
            case FlightLogEvent.LOGGING_RESUME:
                drawEventLine(x, labelY, "Logging resumed", "rgba(50,50,50,0.75)", 3);
            break;
            case FlightLogEvent.SYNC_BEEP:
                drawEventLine(x, labelY, "Arming beep begins", "rgba(0,0,255,0.75)", 3);
            break;
            case FlightLogEvent.GTUNE_CYCLE_RESULT:
                drawEventLine(x, labelY, "GTune result - axis:" + event.data.axis + " gyroAVG:" + event.data.gyroAVG + " newP:" + event.data.newP, "rgba(255,255,255,0.5)");
            break;
            case FlightLogEvent.INFLIGHT_ADJUSTMENT:
                drawEventLine(x, labelY, event.data.name + " = " + event.data.value, "rgba(0,255,255,0.5)", 2);
            break;
            default:
                drawEventLine(x);
        }
        
    }
    
    function drawEvents(chunks) {
        var 
            /* 
             * Also draw events that are a little left of the window, so that their labels don't suddenly 
             * disappear when they scroll out of view:
             */ 
            BEGIN_MARGIN_MICROSECONDS = 100000, 
            shouldSetFont = true,
            sequenceNum = 0;
        
        for (var i = 0; i < chunks.length; i++) {
            var events = chunks[i].events;
            
            for (var j = 0; j < events.length; j++) {
                if (events[j].time > windowEndTime) {
                    return;
                }
                
                if (events[j].time >= windowStartTime - BEGIN_MARGIN_MICROSECONDS) {
                    // Avoid setting the font if we don't draw any events
                    if (shouldSetFont) {
                        canvasContext.fillStyle = "rgba(255, 255, 255, 0.8)";
                        canvasContext.font = drawingParams.fontSizeEventLabel + "pt " + DEFAULT_FONT_FACE;
                        shouldSetFont = false;
                    }
                    
                    drawEvent(events[j], sequenceNum++);
                }
            }
        }
    }
    
    /**
     *  Mark the in/out of the video region (if present) and dim the view outside this region
     */
    function drawInOutRegion() {
        if (inTime !== false && inTime >= windowStartTime || outTime !== false && outTime < windowEndTime) {
            var
                inMarkerX = inTime === false ? false : timeToCanvasX(inTime),
                outMarkerX = outTime === false ? false : timeToCanvasX(outTime); 

            canvasContext.fillStyle = "rgba(200,200,200,0.4)";
            
            if (inTime !== false && inTime >= windowStartTime) {
                canvasContext.fillRect(0, 0, Math.min(inMarkerX, canvas.width), canvas.height);
            } 
            
            if (outTime !== false && outTime < windowEndTime) {
                var
                    outMarkerXClipped = Math.max(outMarkerX, 0);
                canvasContext.fillRect(outMarkerXClipped, 0, canvas.width - outMarkerXClipped, canvas.height);
            }
            
            if (inMarkerX !== false && inMarkerX >= 0 && inMarkerX <= canvas.width || outMarkerX !== false && outMarkerX >= 0 && outMarkerX <= canvas.width) {
                canvasContext.strokeStyle = 'rgb(200,200,200)';
                canvasContext.lineWidth = 4;
    
                if (inMarkerX !== false && inMarkerX >= 0 && inMarkerX <= canvas.width) {
                    canvasContext.beginPath();
                    canvasContext.moveTo(inMarkerX, 0);
                    canvasContext.lineTo(inMarkerX, canvas.height);
                    canvasContext.stroke();
                }
    
                if (outMarkerX !== false && outMarkerX >= 0 && outMarkerX <= canvas.width) {
                    canvasContext.beginPath();
                    canvasContext.moveTo(outMarkerX, 0);
                    canvasContext.lineTo(outMarkerX, canvas.height);
                    canvasContext.stroke();
                }
            }
        }
    }

    function computeDrawingParameters() {
        var
            fontSizeBase = Math.max(10, canvas.height / 60),
            
            newParams = {
                fontSizeCurrentValueLabel: fontSizeBase * 1.0,
                fontSizePIDTableLabel:     fontSizeBase * 3.4,
                fontSizeAxisLabel:         fontSizeBase * 0.9,
                fontSizeFrameLabel:        fontSizeBase * 0.9,
                fontSizeEventLabel:        fontSizeBase * 0.8,
                
                // We're concerned about the horizontal span of this text too: 
                fontSizeCommandStickLabel: canvas.width < 500 ? 0 : Math.min(fontSizeBase, canvas.width / 60) * 1.0,
                commandStickLabelMargin:   Math.min(canvas.width / 80, 8),
                
                plotLineWidth:             Math.max(1.25, canvas.height / 400),
            };

        /* Need enough space between sticks for the pitch axis label to fit */
        newParams.stickSpacing = newParams.fontSizeCommandStickLabel * 4 + newParams.commandStickLabelMargin * 2;
        
        drawingParams = extend(drawingParams, newParams);
    }
    
    this.resize = function(width, height) {
        canvas.width = width;
        canvas.height = height;
        
        if (craft2D) {
            craft2D.resize(canvas.height / 4);
        } else if (craft3D) {
            var
                craftSize;
            
            craftSize = Math.min(canvas.height * CRAFT_POSITION_Y_PROPORTION * 2, canvas.width / 2.5);
            
            craft3D.resize(craftSize, craftSize);
            
            // Recenter the craft canvas in the top left corner
            $(craftCanvas).css({
                left: Math.min(canvas.height * CRAFT_POSITION_Y_PROPORTION - craftSize / 2, canvas.width / 4 - craftSize / 2) + "px",
                top: (canvas.height * CRAFT_POSITION_Y_PROPORTION - craftSize / 2) + "px",
            });
        }
        
        computeDrawingParameters();
    };
    
    this.render = function(windowCenterTimeMicros) {
        windowCenterTime = windowCenterTimeMicros;
        windowStartTime = windowCenterTime - windowWidthMicros / 2;
        windowEndTime = windowStartTime + windowWidthMicros;
        
        if (options.eraseBackground) {
            canvasContext.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        var 
            chunks = flightLog.getSmoothedChunksInTimeRange(windowStartTime, windowEndTime),
            startChunkIndex, startFrameIndex,
            i, j;
        
        if (chunks.length) {
            //Find the first sample that lies inside the window
            for (startFrameIndex = 0; startFrameIndex < chunks[0].frames.length; startFrameIndex++) {
                if (chunks[0].frames[startFrameIndex][FlightLogParser.prototype.FLIGHT_LOG_FIELD_INDEX_TIME] >= windowStartTime) {
                    break;
                }
            }
            
            // Pick the sample before that to begin plotting from
            if (startFrameIndex > 0)
                startFrameIndex--;
            
            // Plot graphs
            for (i = 0; i < graphs.length; i++) {
                var 
                    graph = graphs[i];
            
                canvasContext.save();
                {
                    canvasContext.translate(0, canvas.height * graph.y);
                    
                    drawAxisLine();
                    
                    for (j = 0; j < graph.fields.length; j++) {
                        var field = graph.fields[j];
                        
                        plotField(chunks, startFrameIndex, field.index, field.curve, canvas.height * graph.height / 2, 
                            field.color ? field.color : GraphConfig.PALETTE[j % GraphConfig.PALETTE.length]);
                    }
                    
                    if (graph.label) {
                        drawAxisLabel(graph.label);
                    }
                }
                canvasContext.restore();
            }
            
            //Draw a bar highlighting the current time if we are drawing any graphs
            if (graphs.length) {
                var 
                    centerX = canvas.width / 2;

                canvasContext.strokeStyle = 'rgba(255, 64, 64, 0.2)';
                canvasContext.lineWidth = 10;

                canvasContext.beginPath();
                canvasContext.moveTo(centerX, 0);
                canvasContext.lineTo(centerX, canvas.height);
                canvasContext.stroke();
            }
            
            // Draw events
            drawEvents(chunks);
            
            // Draw details at the current time
            var
                centerFrame = flightLog.getSmoothedFrameAtTime(windowCenterTime);
            
            if (centerFrame) {
                if (options.drawSticks) {
                    canvasContext.save();
                    
                    canvasContext.translate(0.75 * canvas.width, COMMAND_STICK_POSITION_Y_PROPORTION * canvas.height);
                    
                    drawCommandSticks(centerFrame);
                    
                    canvasContext.restore();
                }
                
                if (options.drawTime) {
                    drawFrameLabel(centerFrame[FlightLogParser.prototype.FLIGHT_LOG_FIELD_INDEX_ITERATION], Math.round((windowCenterTime - flightLog.getMinTime()) / 1000));
                }
                
                if (options.drawCraft == '3D') {
                    craft3D.render(centerFrame, flightLog.getMainFieldIndexes());
                } else if (options.drawCraft == '2D') {
                    canvasContext.save();
                
                    canvasContext.translate(0.25 * canvas.width, 0.20 * canvas.height);
                    canvasContext.font = drawingParams.fontSizeCurrentValueLabel + "pt " + DEFAULT_FONT_FACE;

                    craft2D.render(canvasContext, centerFrame, flightLog.getMainFieldIndexes());
                    
                    canvasContext.restore();
                }
            }
        }
        
        drawInOutRegion();
    };
    
    function refreshGraphConfig() {
        var 
            smoothing = {},
            heightSum = 0, allocatedHeight, graphHeight,
            i, graph;
        
        graphs = jQuery.extend(true, [], graphConfig.getGraphs());
        
        for (i = 0; i < graphs.length; i++) {
            graph = graphs[i];
            
            heightSum += graph.height ? graph.height : 1.0;
            
            for (var j = 0; j < graphs[i].fields.length; j++) {
                var field = graphs[i].fields[j];
                
                field.index = flightLog.getMainFieldIndexByName(field.name);
                
                // Convert the field's curve settings into an actual expo curve object:
                field.curve = new ExpoCurve(field.curve.offset, field.curve.power, field.curve.inputRange, 
                    field.curve.outputRange, field.curve.steps); 
                
                if (field.smoothing > 0) {
                    smoothing[field.index] = field.smoothing;
                }
            }
        }
        
        // Lay out the graphs vertically downwards in order
        allocatedHeight = 0;
        for (i = 0; i < graphs.length; i++) {
            graph = graphs[i];
            
            graphHeight = graph.height / heightSum;
            
            graph.y = allocatedHeight + graphHeight / 2;
            
            allocatedHeight += graphHeight;
        }
        
        // Scale the graph heights so they don't overlap
        for (i = 0; i < graphs.length; i++) {
            graph = graphs[i];

            graph.height = graph.height / heightSum * 0.95;
        }
    
        flightLog.setFieldSmoothing(smoothing);
    }
    
    function initializeCraftModel() {
        // Ensure drawCraft is a valid value
        if (["2D", "3D"].indexOf(options.drawCraft) == -1) {
            options.drawCraft = false;
        }
        
        if (options.drawCraft == '3D') {
            if (craftCanvas) {
                try {
                    craft3D = new Craft3D(flightLog, craftCanvas, idents.motorColors);
                } catch (e) {
                    //WebGL not supported, fall back to 2D rendering
                    options.drawCraft = '2D';
                }
            } else {
                //Dedicated craft canvas not provided so we can't render in 3D, fall back
                options.drawCraft = '2D';
            }
        }
        
        if (options.drawCraft == '2D') {
            if (craftCanvas) {
                craftCanvas.width = 0;
                craftCanvas.height = 0;
            }
            craft2D = new Craft2D(flightLog, canvas, idents.motorColors, decide2DCraftParameters());
        }
    }
    
    this.destroy = function() {
        $(canvas).off("mousedown", onMouseDown);
    };
    
    this.setGraphZoom = function(zoom) {
        windowWidthMicros = Math.round(WINDOW_WIDTH_MICROS_DEFAULT / zoom);
    };
    
    this.setInTime = function(time) {
        inTime = time;
        
        if (outTime <= inTime) {
            outTime = false;
        }
    };

    this.setOutTime = function(time) {
        outTime = time;
        
        if (inTime >= outTime) {
            inTime = false;
        }
    };

    // Use defaults for any options not provided
    options = extend(defaultOptions, options || {});
    
    identifyFields();

    initializeCraftModel();

    //Handle dragging events
    $(canvas).on("mousedown", onMouseDown);
    
    graphConfig.addListener(refreshGraphConfig);
    refreshGraphConfig();
    
    this.resize(canvas.width, canvas.height);
}
