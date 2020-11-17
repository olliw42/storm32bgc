"use strict";

function VideoExportDialog(dialog, onSave) {
    var
        DIALOG_MODE_SETTINGS = 0,
        DIALOG_MODE_IN_PROGRESS = 1,
        DIALOG_MODE_COMPLETE = 2,
        
        currentGraphConfig,
        flightLogDataArray,
        dialogMode,
        
        videoRenderer = false,
        
        videoDuration = $(".video-duration", dialog),
        progressBar = $("progress", dialog),
        progressRenderedFrames = $(".video-export-rendered-frames", dialog),
        progressRemaining = $(".video-export-remaining", dialog),
        progressSize = $(".video-export-size", dialog),
        fileSizeWarning = $(".video-export-size + .alert", dialog),

        renderStartTime,
        lastEstimatedTimeMsec,
        
        that = this;

    function leftPad(value, pad, width) {
        // Coorce value to string
        value = value + "";
        
        while (value.length < width) {
            value = pad + value;
        }
        
        return value;
    }
    
    function formatTime(secs) {
        var
            mins = Math.floor(secs / 60),
            secs = secs % 60,
            
            hours = Math.floor(mins / 60);
        
        mins = mins % 60;
        
        if (hours) {
            return hours + ":" + leftPad(mins, "0", 2) + ":" + leftPad(secs, "0", 2);
        } else {
            return mins + ":" + leftPad(secs, "0", 2);
        }
    }
    
    function formatFilesize(bytes) {
        var
            megs = Math.round(bytes / (1024 * 1024));
        
        return megs + "MB";
    }
    
    function setDialogMode(mode) {
        dialogMode = mode;
        
        var
            settingClasses = [
                "video-export-mode-settings", 
                "video-export-mode-progress", 
                "video-export-mode-complete"
            ];
        
        dialog
            .removeClass(settingClasses.join(" "))
            .addClass(settingClasses[mode]);
        
        $(".video-export-dialog-start").toggle(mode == DIALOG_MODE_SETTINGS);
        $(".video-export-dialog-cancel").toggle(mode != DIALOG_MODE_COMPLETE);
        $(".video-export-dialog-close").toggle(mode == DIALOG_MODE_COMPLETE);
        
        var 
            title = "Export video";
        
        switch (mode) {
            case DIALOG_MODE_IN_PROGRESS:
                title = "Rendering video...";
            break;
            case DIALOG_MODE_COMPLETE:
                title = "Video rendering complete!";
            break;
        }
        
        $(".modal-title", dialog).text(title);
    }

    function populateConfig(videoConfig) {
        if (videoConfig.frameRate) {
            $(".video-frame-rate").val(videoConfig.frameRate);
        }
        if (videoConfig.videoDim !== undefined) {
            // Look for a value in the UI which closely matches the stored one (allows for floating point inaccuracy)
            $(".video-dim option").each(function() {
                var
                    thisVal = parseFloat($(this).attr('value'));
                
                if (Math.abs(videoConfig.videoDim - thisVal) < 0.05) {
                    $(".video-dim").val($(this).attr('value'));
                }
            });
        }
        if (videoConfig.width) {
            $(".video-resolution").val(videoConfig.width + "x" + videoConfig.height);
        }
    }
    
    function convertUIToVideoConfig() {
        var 
            videoConfig = {
                frameRate: parseInt($(".video-frame-rate", dialog).val(), 10),
                videoDim: parseFloat($(".video-dim", dialog).val())
            },
            resolution;
        
        resolution = $(".video-resolution", dialog).val();
        
        videoConfig.width = parseInt(resolution.split("x")[0], 10);
        videoConfig.height = parseInt(resolution.split("x")[1], 10);

        return videoConfig;
    }

    this.show = function(flightLog, logParameters, videoConfig) {
        setDialogMode(DIALOG_MODE_SETTINGS);
        
        if (!("inTime" in logParameters) || logParameters.inTime === false) {
            logParameters.inTime = flightLog.getMinTime();
        }
        
        if (!("outTime" in logParameters) || logParameters.outTime === false) {
            logParameters.outTime = flightLog.getMaxTime();
        }
        
        videoDuration.text(formatTime(Math.round((logParameters.outTime - logParameters.inTime) / 1000000)));
        
        $(".jumpy-video-note").toggle(!!logParameters.flightVideo);
        
        dialog.modal('show');
        
        this.flightLog = flightLog;
        this.logParameters = logParameters;
        
        populateConfig(videoConfig);
    };
 
    $(".video-export-dialog-start").click(function(e) {
        var
            lastWrittenBytes = 0,
            videoConfig = convertUIToVideoConfig();
        
        // Send our video config to our host to be saved for next time:
        onSave(videoConfig);
        
        videoRenderer = new FlightLogVideoRenderer(that.flightLog, that.logParameters, videoConfig, {
            onProgress: function(frameIndex, frameCount) {
                progressBar.prop('max', frameCount - 1);
                progressBar.prop('value', frameIndex);
                
                progressRenderedFrames.text((frameIndex + 1) + " / " + frameCount + " (" + ((frameIndex + 1) / frameCount * 100).toFixed(1) + "%)");
                
                if (frameIndex > 0) {
                    var
                        elapsedTimeMsec = Date.now() - renderStartTime,
                        estimatedTimeMsec = elapsedTimeMsec * frameCount / frameIndex;
                    
                    if (lastEstimatedTimeMsec === false) {
                        lastEstimatedTimeMsec = estimatedTimeMsec; 
                    } else {
                        lastEstimatedTimeMsec = lastEstimatedTimeMsec * 0.0 + estimatedTimeMsec * 1.0;
                    }
                    
                    var
                        estimatedRemaining = Math.max(Math.round((lastEstimatedTimeMsec - elapsedTimeMsec) / 1000), 0);
                    
                    progressRemaining.text(formatTime(estimatedRemaining));
                    
                    var
                        writtenBytes = videoRenderer.getWrittenSize(),
                        estimatedBytes = Math.round(frameCount / frameIndex * writtenBytes);
                    
                    /* 
                     * Only update the filesize estimate when a block is written (avoids the estimated filesize slowly 
                     * decreasing between blocks)
                     */
                    if (writtenBytes != lastWrittenBytes) {
                        lastWrittenBytes = writtenBytes;
                        
                        if (writtenBytes > 1000000) { // Wait for the first significant chunk to be written (don't use the tiny header as a size estimate)
                            progressSize.text(formatFilesize(writtenBytes) + " / " + formatFilesize(estimatedBytes));
                            
                            fileSizeWarning.toggle(!videoRenderer.willWriteDirectToDisk() && estimatedBytes >= 475 * 1024 * 1024);
                        }
                    }
                }
            },
            onComplete: function(success, frameCount) {
                if (success) {
                    $(".video-export-result").text("Rendered " + frameCount + " frames in " + formatTime(Math.round((Date.now() - renderStartTime) / 1000)));
                    setDialogMode(DIALOG_MODE_COMPLETE);
                } else {
                    dialog.modal('hide');
                }
                // Free up any memory still held by the video renderer
                if (videoRenderer) {
                    videoRenderer = false;
                }
            }
        });
        
        progressBar.prop('value', 0);
        progressRenderedFrames.text('');
        progressRemaining.text('');
        progressSize.text('Calculating...');
        fileSizeWarning.hide();
        
        setDialogMode(DIALOG_MODE_IN_PROGRESS);
        
        renderStartTime = Date.now();
        lastEstimatedTimeMsec = false;
        videoRenderer.start();
        
        e.preventDefault();
    });
    
    $(".video-export-dialog-cancel").click(function(e) {
        if (videoRenderer) {
            videoRenderer.cancel();
        }
    });
    
    dialog.modal({
        show: false,
        backdrop: "static" // Don't allow a click on the backdrop to close the dialog
    });
}