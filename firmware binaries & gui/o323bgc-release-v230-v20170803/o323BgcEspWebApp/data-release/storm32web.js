//STorM32 Web App v0.27b
// (c) www.OlliW.eu 2017

/*TODO:
- always do a read before a write ?
- check validity after a write
- version check, as in GUI
- several tries before alert in updateRead, updateStatus
*/


'use strict';


//http://geekswithblogs.net/lorint/archive/2006/03/07/71625.aspx
//https://stackoverflow.com/questions/1018705/how-to-detect-timeout-on-an-ajax-xmlhttprequest-call-in-the-browser
function ajaxDo(type, url, content, func) {

    if( XhttpTransferInProgress ){ alert("A Xhttp transfer is currently in progress. Wait and repeat."); return; }
    XhttpTransferInProgress = true;
    
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if( this.readyState == 4 ){ 
            clearTimeout(xhttpTimeout); 
            if( (this.readyState == 4) && (this.status == 200) ){ 
                ConnectionIsValid = true; 
                func(this); 
            }else{
                ConnectionIsValid = false;
                setPAllToInvalid();                
            }
        }
    };
    xhttp.open(type, url, true); //xhttp.open('POST', url, true); //xhttp.open('GET', url, true);
    if( content.length ) xhttp.send(content); else xhttp.send();
    // timeout to abort in 5 seconds
    function ajaxTimeout(){
        xhttp.abort();
        ConnectionIsValid = false;
        setPAllToInvalid();
        alert("Xhttp request timed out");
    }    
    var xhttpTimeout = setTimeout(ajaxTimeout,3000);
    
    XhttpTransferInProgress = false;
}


function ajaxPost(url, content, func) {
    ajaxDo('POST', url, content, func);
}

function ajaxGet(url, content, func) {
    ajaxDo('GET', url, content, func);
}


//-----------------------------------------------------
// parameter description
//-----------------------------------------------------

//capability constants
var BOARD_CAPABILITY_FOC           =  0x0100;

var FocIsEnabled = false;

//this is a flag to avoid that more than one xhhtp transfer is going on at a time
// is this really working????
var XhttpTransferInProgress = false;

//this is flag tells about the connection to the ESP and/or STorM32
// it holds the success result of the last XhttpRequest, as well as that of the returned resposne, if it was 'o' or not
var ConnectionIsValid = false;

//this is the string of hex received via read, i.e. g
// it is needed to keep the scripts, and to keep values not available or changed
// it has to be maintained
var PValues = '';

//this is to maintain the status of the PValues
var INVALID = 0;
var VALID = 1;
var MODIFIED = 2;
var PStatus = INVALID;  //this can be invalid = 0, valid = 1, modified; 

// L229
var P =
{
/*
  'FirmwareVersion' : {'default' : '', 'column' : 1, 'unit' : '', 'size' : 16, 'hidden' : 0, 
                       'page' : 'dashboard', 'type' : 'OPTTYPE_STR+OPTTYPE_READONLY', 'name' : 'Firmware Version'},
  'GyroLPF' : {'steps' : 1, 'default' : 1, 'adr' : 12, 'max' : 6, 'len' : 0, 
               'page' : 'pid', 'min' : 0, 
               'choices' : ['off', '1.5 ms', '3.0 ms', '4.5 ms', '6.0 ms', '7.5 ms', '9 ms'], 
               'type' : 'OPTTYPE_LISTA', 'unit' : '', 'size' : 1, 'hidden' : 0, 'pos' : [1, 1], 
               'name' : 'Gyro LPF', 'ppos' : 0},
  'PitchP' : {'steps' : 10, 'default' : 400, 'adr' : 0, 'max' : 3000, 
              'page' : 'pid', 'min' : 0, 'len' : 5, 'size' : 2, 'ppos' : 2, 
              'type' : 'OPTTYPE_UI', 'hidden' : 0, 'pos' : [2, 1], 
              'name' : 'Pitch P', 'unit' : ''},
*/              
  'FirmwareVersion' : {'default' : '', 'type' : 'OPTTYPE_STR+OPTTYPE_READONLY', 'name' : 'Firmware Version', 'column' : 1, 'hidden' : 0, 'steps' : 1, 'page' : 'dashboard', 'size' : 16, 'unit' : ''},
  'Board' : {'default' : '', 'type' : 'OPTTYPE_STR+OPTTYPE_READONLY', 'name' : 'Board', 'hidden' : 0, 'steps' : 1, 'page' : 'dashboard', 'size' : 16, 'unit' : ''},
  'Name' : {'default' : '', 'type' : 'OPTTYPE_STR+OPTTYPE_READONLY', 'name' : 'Name', 'hidden' : 0, 'steps' : 1, 'page' : 'dashboard', 'size' : 16, 'unit' : ''},
  'GyroLPF' : {'default' : 1, 'name' : 'Gyro LPF', 'choices' : ['off', '1.5 ms', '3.0 ms', '4.5 ms', '6.0 ms', '7.5 ms', '9 ms'], 'len' : 0, 'steps' : 1, 'max' : 6, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 1], 'page' : 'pid', 'adr' : 12, 'size' : 1, 'unit' : ''},
  'FocGyroLPF' : {'default' : 1, 'name' : 'Foc Gyro LPF', 'choices' : ['off', '1.5 ms', '3.0 ms', '4.5 ms', '6.0 ms', '7.5 ms', '9 ms'], 'len' : 0, 'steps' : 1, 'max' : 6, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 1], 'page' : 'pid', 'adr' : 41, 'size' : 1, 'unit' : ''},
  'Imu2FeedForwardLPF' : {'default' : 1, 'name' : 'Imu2 FeedForward LPF', 'choices' : ['off', '1.5 ms', '4 ms', '10 ms', '22 ms', '46 ms', '94 ms'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 72, 'size' : 1, 'unit' : ''},
  'VoltageCorrection' : {'default' : 0, 'name' : 'Voltage Correction', 'pos' : [1, 4], 'len' : 7, 'steps' : 1, 'max' : 200, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 75, 'size' : 2, 'unit' : '%'},
  'RollYawPDMixing' : {'default' : 0, 'name' : 'Roll Yaw PD Mixing', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 73, 'size' : 2, 'unit' : '%'},
  'PitchP' : {'default' : 400, 'name' : 'Pitch P', 'pos' : [2, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 0, 'size' : 2, 'unit' : ''},
  'PitchI' : {'default' : 1000, 'name' : 'Pitch I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 1, 'size' : 2, 'unit' : ''},
  'PitchD' : {'default' : 500, 'name' : 'Pitch D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 2, 'size' : 2, 'unit' : ''},
  'PitchMotorVmax' : {'default' : 150, 'name' : 'Pitch Motor Vmax', 'len' : 5, 'steps' : 1, 'max' : 255, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 3, 'size' : 2, 'unit' : ''},
  'RollP' : {'default' : 400, 'name' : 'Roll P', 'pos' : [3, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 4, 'size' : 2, 'unit' : ''},
  'RollI' : {'default' : 1000, 'name' : 'Roll I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 5, 'size' : 2, 'unit' : ''},
  'RollD' : {'default' : 500, 'name' : 'Roll D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 6, 'size' : 2, 'unit' : ''},
  'RollMotorVmax' : {'default' : 150, 'name' : 'Roll Motor Vmax', 'len' : 5, 'steps' : 1, 'max' : 255, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 7, 'size' : 2, 'unit' : ''},
  'YawP' : {'default' : 400, 'name' : 'Yaw P', 'pos' : [4, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 8, 'size' : 2, 'unit' : ''},
  'YawI' : {'default' : 1000, 'name' : 'Yaw I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 9, 'size' : 2, 'unit' : ''},
  'YawD' : {'default' : 500, 'name' : 'Yaw D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 10, 'size' : 2, 'unit' : ''},
  'YawMotorVmax' : {'default' : 150, 'name' : 'Yaw Motor Vmax', 'len' : 5, 'steps' : 1, 'max' : 255, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pid', 'adr' : 11, 'size' : 2, 'unit' : ''},
  'FocPitchP' : {'default' : 400, 'name' : 'Foc Pitch P', 'pos' : [2, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 23, 'size' : 2, 'unit' : ''},
  'FocPitchI' : {'default' : 100, 'name' : 'Foc Pitch I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 24, 'size' : 2, 'unit' : ''},
  'FocPitchD' : {'default' : 2000, 'name' : 'Foc Pitch D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 25, 'size' : 2, 'unit' : ''},
  'FocPitchK' : {'default' : 10, 'name' : 'Foc Pitch K', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 1, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 26, 'size' : 2, 'unit' : ''},
  'FocRollP' : {'default' : 400, 'name' : 'Foc Roll P', 'pos' : [3, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 29, 'size' : 2, 'unit' : ''},
  'FocRollI' : {'default' : 100, 'name' : 'Foc Roll I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 30, 'size' : 2, 'unit' : ''},
  'FocRollD' : {'default' : 2000, 'name' : 'Foc Roll D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 31, 'size' : 2, 'unit' : ''},
  'FocRollK' : {'default' : 10, 'name' : 'Foc Roll K', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 1, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 32, 'size' : 2, 'unit' : ''},
  'FocYawP' : {'default' : 400, 'name' : 'Foc Yaw P', 'pos' : [4, 1], 'len' : 5, 'steps' : 10, 'max' : 3000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pid', 'adr' : 35, 'size' : 2, 'unit' : ''},
  'FocYawI' : {'default' : 100, 'name' : 'Foc Yaw I', 'len' : 7, 'steps' : 50, 'max' : 32000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 36, 'size' : 2, 'unit' : ''},
  'FocYawD' : {'default' : 2000, 'name' : 'Foc Yaw D', 'len' : 3, 'steps' : 50, 'max' : 8000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 4, 'hidden' : 0, 'page' : 'pid', 'adr' : 37, 'size' : 2, 'unit' : ''},
  'FocYawK' : {'default' : 10, 'name' : 'Foc Yaw K', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 1, 'ppos' : 1, 'hidden' : 0, 'page' : 'pid', 'adr' : 38, 'size' : 2, 'unit' : ''},
  'PanModeControl' : {'default' : 0, 'name' : 'Pan Mode Control', 'column' : 1, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 79, 'size' : 1, 'unit' : ''},
  'PanModeDefaultSetting' : {'default' : 0, 'name' : 'Pan Mode Default Setting', 'choices' : ['hold hold pan', 'hold hold hold', 'pan pan pan', 'pan hold hold', 'pan hold pan', 'hold pan pan', 'off'], 'len' : 0, 'steps' : 1, 'max' : 5, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 80, 'size' : 1, 'unit' : ''},
  'PanModeSetting1' : {'default' : 1, 'name' : 'Pan Mode Setting #1', 'choices' : ['hold hold pan', 'hold hold hold', 'pan pan pan', 'pan hold hold', 'pan hold pan', 'hold pan pan', 'off'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 81, 'size' : 1, 'unit' : ''},
  'PanModeSetting2' : {'default' : 4, 'name' : 'Pan Mode Setting #2', 'choices' : ['hold hold pan', 'hold hold hold', 'pan pan pan', 'pan hold hold', 'pan hold pan', 'hold pan pan', 'off'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 82, 'size' : 1, 'unit' : ''},
  'PanModeSetting3' : {'default' : 2, 'name' : 'Pan Mode Setting #3', 'choices' : ['hold hold pan', 'hold hold hold', 'pan pan pan', 'pan hold hold', 'pan hold pan', 'hold pan pan', 'off'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 83, 'size' : 1, 'unit' : ''},
  'PitchPan' : {'default' : 20, 'name' : 'Pitch Pan', 'column' : 2, 'len' : 5, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 84, 'size' : 2, 'unit' : ''},
  'PitchPanDeadband' : {'default' : 0, 'name' : 'Pitch Pan Deadband', 'pos' : [2, 3], 'len' : 5, 'steps' : 10, 'max' : 600, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 85, 'size' : 2, 'unit' : '\u00b0'},
  'PitchPanExpo' : {'default' : 0, 'name' : 'Pitch Pan Expo', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 86, 'size' : 2, 'unit' : '%'},
  'RollPan' : {'default' : 20, 'name' : 'Roll Pan', 'column' : 3, 'len' : 5, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 87, 'size' : 2, 'unit' : ''},
  'RollPanDeadband' : {'default' : 0, 'name' : 'Roll Pan Deadband', 'pos' : [3, 3], 'len' : 5, 'steps' : 10, 'max' : 600, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 88, 'size' : 2, 'unit' : '\u00b0'},
  'RollPanExpo' : {'default' : 0, 'name' : 'Roll Pan Expo', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 89, 'size' : 2, 'unit' : '%'},
  'YawPan' : {'default' : 20, 'name' : 'Yaw Pan', 'column' : 4, 'len' : 5, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 90, 'size' : 2, 'unit' : ''},
  'YawPanDeadband' : {'default' : 50, 'name' : 'Yaw Pan Deadband', 'pos' : [4, 3], 'len' : 5, 'steps' : 5, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 91, 'size' : 2, 'unit' : '\u00b0'},
  'YawPanExpo' : {'default' : 0, 'name' : 'Yaw Pan Expo', 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'pan', 'adr' : 92, 'size' : 2, 'unit' : '%'},
  'YawPanDeadbandLPF' : {'default' : 150, 'name' : 'Yaw Pan Deadband LPF', 'len' : 5, 'steps' : 5, 'max' : 300, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'pan', 'adr' : 93, 'size' : 2, 'unit' : 's'},
  'YawPanDeadbandHysteresis' : {'default' : 0, 'name' : 'Yaw Pan Deadband Hysteresis', 'pos' : [4, 6], 'len' : 5, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'pan', 'adr' : 94, 'size' : 2, 'unit' : '\u00b0'},
  'RcDeadBand' : {'default' : 10, 'name' : 'Rc Dead Band', 'len' : 0, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 96, 'size' : 2, 'unit' : 'us'},
  'RcHysteresis' : {'default' : 5, 'name' : 'Rc Hysteresis', 'len' : 0, 'steps' : 1, 'max' : 50, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 97, 'size' : 2, 'unit' : 'us'},
  'RcPitchTrim' : {'default' : 0, 'name' : 'Rc Pitch Trim', 'pos' : [1, 4], 'len' : 0, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_SI', 'min' : -100, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 104, 'size' : 2, 'unit' : 'us'},
  'RcRollTrim' : {'default' : 0, 'name' : 'Rc Roll Trim', 'len' : 0, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_SI', 'min' : -100, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 111, 'size' : 2, 'unit' : 'us'},
  'RcYawTrim' : {'default' : 0, 'name' : 'Rc Yaw Trim', 'len' : 0, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_SI', 'min' : -100, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 118, 'size' : 2, 'unit' : 'us'},
  'RcPitch' : {'default' : 0, 'name' : 'Rc Pitch', 'column' : 2, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 102, 'size' : 1, 'unit' : ''},
  'RcPitchMode' : {'default' : 0, 'name' : 'Rc Pitch Mode', 'choices' : ['absolute', 'relative', 'absolute centered'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 103, 'size' : 1, 'unit' : ''},
  'RcPitchMin' : {'default' : -250, 'name' : 'Rc Pitch Min', 'len' : 0, 'steps' : 5, 'max' : 1200, 'type' : 'OPTTYPE_SI', 'min' : -1200, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 105, 'size' : 2, 'unit' : '\u00b0'},
  'RcPitchMax' : {'default' : 250, 'name' : 'Rc Pitch Max', 'len' : 0, 'steps' : 5, 'max' : 1200, 'type' : 'OPTTYPE_SI', 'min' : -1200, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 106, 'size' : 2, 'unit' : '\u00b0'},
  'RcPitchSpeedLimit' : {'default' : 400, 'name' : 'Rc Pitch Speed Limit', 'len' : 0, 'steps' : 5, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 107, 'size' : 2, 'unit' : '\u00b0/s'},
  'RcPitchAccelLimit' : {'default' : 300, 'name' : 'Rc Pitch Accel Limit', 'len' : 0, 'steps' : 10, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 3, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 108, 'size' : 2, 'unit' : ''},
  'RcRoll' : {'default' : 0, 'name' : 'Rc Roll', 'column' : 3, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 109, 'size' : 1, 'unit' : ''},
  'RcRollMode' : {'default' : 0, 'name' : 'Rc Roll Mode', 'choices' : ['absolute', 'relative', 'absolute centered'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 110, 'size' : 1, 'unit' : ''},
  'RcRollMin' : {'default' : -250, 'name' : 'Rc Roll Min', 'len' : 0, 'steps' : 5, 'max' : 450, 'type' : 'OPTTYPE_SI', 'min' : -450, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 112, 'size' : 2, 'unit' : '\u00b0'},
  'RcRollMax' : {'default' : 250, 'name' : 'Rc Roll Max', 'len' : 0, 'steps' : 5, 'max' : 450, 'type' : 'OPTTYPE_SI', 'min' : -450, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 113, 'size' : 2, 'unit' : '\u00b0'},
  'RcRollSpeedLimit' : {'default' : 400, 'name' : 'Rc Roll Speed Limit', 'len' : 0, 'steps' : 5, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 114, 'size' : 2, 'unit' : '\u00b0/s'},
  'RcRollAccelLimit' : {'default' : 300, 'name' : 'Rc Roll Accel Limit', 'len' : 0, 'steps' : 10, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 3, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 115, 'size' : 2, 'unit' : ''},
  'RcYaw' : {'default' : 0, 'name' : 'Rc Yaw', 'column' : 4, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 116, 'size' : 1, 'unit' : ''},
  'RcYawMode' : {'default' : 0, 'name' : 'Rc Yaw Mode', 'choices' : ['absolute', 'relative', 'absolute centered', 'relative turn around'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 117, 'size' : 1, 'unit' : ''},
  'RcYawMin' : {'default' : -250, 'name' : 'Rc Yaw Min', 'len' : 0, 'steps' : 10, 'max' : 2700, 'type' : 'OPTTYPE_SI', 'min' : -2700, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 119, 'size' : 2, 'unit' : '\u00b0'},
  'RcYawMax' : {'default' : 250, 'name' : 'Rc Yaw Max', 'len' : 0, 'steps' : 10, 'max' : 2700, 'type' : 'OPTTYPE_SI', 'min' : -2700, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 120, 'size' : 2, 'unit' : '\u00b0'},
  'RcYawSpeedLimit' : {'default' : 400, 'name' : 'Rc Yaw Speed Limit', 'len' : 0, 'steps' : 5, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 121, 'size' : 2, 'unit' : '\u00b0/s'},
  'RcYawAccelLimit' : {'default' : 300, 'name' : 'Rc Yaw Accel Limit', 'len' : 0, 'steps' : 10, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 3, 'hidden' : 0, 'page' : 'rcinputs', 'adr' : 122, 'size' : 2, 'unit' : ''},
  'Standby' : {'default' : 0, 'name' : 'Standby', 'column' : 1, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 123, 'size' : 1, 'unit' : ''},
  'RecenterCamera' : {'default' : 0, 'name' : 'Re-center Camera', 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 3], 'page' : 'functions', 'adr' : 124, 'size' : 1, 'unit' : ''},
  'IRCameraControl' : {'default' : 0, 'name' : 'IR Camera Control', 'column' : 2, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 125, 'size' : 1, 'unit' : ''},
  'CameraModel' : {'default' : 0, 'name' : 'Camera Model', 'choices' : ['Sony Nex', 'Canon', 'Panasonic', 'Nikon', 'Git2 Rc', 'CAMremote'], 'len' : 0, 'steps' : 1, 'max' : 5, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 126, 'size' : 1, 'unit' : ''},
  'IRCameraSetting1' : {'default' : 0, 'name' : 'IR Camera Setting #1', 'choices' : ['shutter', 'shutter delay', 'video on/off'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 127, 'size' : 1, 'unit' : ''},
  'IRCameraSetting2' : {'default' : 2, 'name' : 'IR Camera Setting #2', 'choices' : ['shutter', 'shutter delay', 'video on/off', 'off'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 128, 'size' : 1, 'unit' : ''},
  'TimeInterval' : {'default' : 0, 'name' : 'Time Interval', 'len' : 0, 'steps' : 1, 'max' : 150, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'functions', 'adr' : 129, 'size' : 2, 'unit' : 's'},
  'PwmOutControl' : {'default' : 0, 'name' : 'Pwm Out Control', 'column' : 3, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 130, 'size' : 1, 'unit' : ''},
  'PwmOutMid' : {'default' : 1500, 'name' : 'Pwm Out Mid', 'len' : 0, 'steps' : 1, 'max' : 2100, 'type' : 'OPTTYPE_UI', 'min' : 900, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 131, 'size' : 2, 'unit' : 'us'},
  'PwmOutMin' : {'default' : 1100, 'name' : 'Pwm Out Min', 'len' : 0, 'steps' : 10, 'max' : 2100, 'type' : 'OPTTYPE_UI', 'min' : 900, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 132, 'size' : 2, 'unit' : 'us'},
  'PwmOutMax' : {'default' : 1900, 'name' : 'Pwm Out Max', 'len' : 0, 'steps' : 10, 'max' : 2100, 'type' : 'OPTTYPE_UI', 'min' : 900, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 133, 'size' : 2, 'unit' : 'us'},
  'PwmOutSpeedLimit' : {'default' : 0, 'name' : 'Pwm Out Speed Limit', 'len' : 0, 'steps' : 5, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'functions', 'adr' : 134, 'size' : 2, 'unit' : 'us/s'},
  'Script1Control' : {'default' : 0, 'name' : 'Script1 Control', 'column' : 1, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'scripts', 'adr' : 150, 'size' : 1, 'unit' : ''},
  'Script2Control' : {'default' : 0, 'name' : 'Script2 Control', 'column' : 2, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'scripts', 'adr' : 151, 'size' : 1, 'unit' : ''},
  'Script3Control' : {'default' : 0, 'name' : 'Script3 Control', 'column' : 3, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'scripts', 'adr' : 152, 'size' : 1, 'unit' : ''},
  'Script4Control' : {'default' : 0, 'name' : 'Script4 Control', 'column' : 4, 'choices' : ['off', 'Rc-0', 'Rc-1', 'Rc-2', 'Rc2-0', 'Rc2-1', 'Rc2-2', 'Rc2-3', 'Pot-0', 'Pot-1', 'Pot-2', 'Virtual-1', 'Virtual-2', 'Virtual-3', 'Virtual-4', 'Virtual-5', 'Virtual-6', 'Virtual-7', 'Virtual-8', 'Virtual-9', 'Virtual-10', 'Virtual-11', 'Virtual-12', 'Virtual-13', 'Virtual-14', 'Virtual-15', 'Virtual-16', 'But switch', 'But latch', 'But step', 'Aux-0 switch', 'Aux-1 switch', 'Aux-2 switch', 'Aux-01 switch', 'Aux-012 switch', 'Aux-0 latch', 'Aux-1 latch', 'Aux-2 latch', 'Aux-01 latch', 'Aux-012 latch', 'Aux-0 step', 'Aux-1 step', 'Aux-2 step'], 'len' : 0, 'steps' : 1, 'max' : 42, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'scripts', 'adr' : 153, 'size' : 1, 'unit' : ''},
  'Scripts' : {'default' : '', 'name' : 'Scripts', 'len' : 0, 'steps' : 0, 'max' : 0, 'type' : 'OPTTYPE_SCRIPT', 'min' : 0, 'ppos' : 0, 'hidden' : 1, 'page' : 'scripts', 'adr' : 154, 'size' : 128, 'unit' : ''},
  'Imu2Configuration' : {'default' : 0, 'name' : 'Imu2 Configuration', 'choices' : ['off', 'full', 'full xy'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 53, 'size' : 1, 'unit' : ''},
  'StartupMode' : {'default' : 0, 'name' : 'Startup Mode', 'choices' : ['normal', 'fast'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 4], 'page' : 'setup', 'adr' : 140, 'size' : 1, 'unit' : ''},
  'StartupDelay' : {'default' : 0, 'name' : 'Startup Delay', 'len' : 0, 'steps' : 5, 'max' : 250, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'setup', 'adr' : 141, 'size' : 2, 'unit' : 's'},
  'ImuAHRS' : {'default' : 1000, 'name' : 'Imu AHRS', 'len' : 5, 'steps' : 100, 'max' : 2500, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'setup', 'adr' : 61, 'size' : 2, 'unit' : 's'},
  'VirtualChannelConfiguration' : {'default' : 0, 'name' : 'Virtual Channel Configuration', 'column' : 2, 'choices' : ['off', 'sum ppm 6', 'sum ppm 7', 'sum ppm 8', 'sum ppm 10', 'sum ppm 12', 'spektrum 10 bit', 'spektrum 11 bit', 'sbus', 'hott sumd', 'srxl', 'serial'], 'len' : 0, 'steps' : 1, 'max' : 11, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 77, 'size' : 1, 'unit' : ''},
  'PwmOutConfiguration' : {'default' : 0, 'name' : 'Pwm Out Configuration', 'choices' : ['off', '1520 us 55 Hz', '1520 us 250 Hz'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 78, 'size' : 1, 'unit' : ''},
  'RcPitchOffset' : {'default' : 0, 'name' : 'Rc Pitch Offset', 'pos' : [2, 4], 'len' : 0, 'steps' : 5, 'max' : 1200, 'type' : 'OPTTYPE_SI', 'min' : -1200, 'ppos' : 1, 'hidden' : 0, 'page' : 'setup', 'adr' : 99, 'size' : 2, 'unit' : '\u00b0'},
  'RcRollOffset' : {'default' : 0, 'name' : 'Rc Roll Offset', 'len' : 0, 'steps' : 5, 'max' : 1200, 'type' : 'OPTTYPE_SI', 'min' : -1200, 'ppos' : 1, 'hidden' : 0, 'page' : 'setup', 'adr' : 100, 'size' : 2, 'unit' : '\u00b0'},
  'RcYawOffset' : {'default' : 0, 'name' : 'Rc Yaw Offset', 'len' : 0, 'steps' : 5, 'max' : 1200, 'type' : 'OPTTYPE_SI', 'min' : -1200, 'ppos' : 1, 'hidden' : 0, 'page' : 'setup', 'adr' : 101, 'size' : 2, 'unit' : '\u00b0'},
  'EspConfiguration' : {'default' : 0, 'name' : 'Esp Configuration', 'choices' : ['off', 'uart', 'uart2'], 'len' : 0, 'steps' : 1, 'max' : 2, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [3, 1], 'page' : 'setup', 'adr' : 147, 'size' : 1, 'unit' : ''},
  'LowVoltageLimit' : {'default' : 1, 'name' : 'Low Voltage Limit', 'choices' : ['off', '2.9 V/cell', '3.0 V/cell', '3.1 V/cell', '3.2 V/cell', '3.3 V/cell', '3.4 V/cell', '3.5 V/cell'], 'len' : 0, 'steps' : 1, 'max' : 7, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [3, 4], 'page' : 'setup', 'adr' : 74, 'size' : 1, 'unit' : ''},
  'BeepwithMotors' : {'default' : 0, 'name' : 'Beep with Motors', 'choices' : ['off', 'basic', 'all'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 143, 'size' : 1, 'unit' : ''},
  'NTLogging' : {'default' : 0, 'name' : 'NT Logging', 'choices' : ['off', 'basic', 'basic + pid', 'basic + accgyro', 'basic + accgyro_raw', 'basic + pid + accgyro', 'basic + pid + ag_raw', 'full'], 'len' : 0, 'steps' : 1, 'max' : 7, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 142, 'size' : 1, 'unit' : ''},
  'PitchMotorUsage' : {'default' : 3, 'name' : 'Pitch Motor Usage', 'column' : 4, 'choices' : ['normal', 'level', 'startup pos', 'disabled'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 55, 'size' : 1, 'unit' : ''},
  'RollMotorUsage' : {'default' : 3, 'name' : 'Roll Motor Usage', 'choices' : ['normal', 'level', 'startup pos', 'disabled'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 56, 'size' : 1, 'unit' : ''},
  'YawMotorUsage' : {'default' : 3, 'name' : 'Yaw Motor Usage', 'choices' : ['normal', 'level', 'startup pos', 'disabled'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'setup', 'adr' : 57, 'size' : 1, 'unit' : ''},
  'ImuOrientation' : {'default' : 0, 'name' : 'Imu Orientation', 'choices' : ['no.0 :  z0\u00b0   x  y  z', 'no.1 :  z90\u00b0  -y  x  z', 'no.2 :  z180\u00b0  -x -y  z', 'no.3 :  z270\u00b0   y -x  z', 'no.4 :  x0\u00b0   y  z  x', 'no.5 :  x90\u00b0  -z  y  x', 'no.6 :  x180\u00b0  -y -z  x', 'no.7 :  x270\u00b0   z -y  x', 'no.8 :  y0\u00b0   z  x  y', 'no.9 :  y90\u00b0  -x  z  y', 'no.10 :  y180\u00b0  -z -x  y', 'no.11 :  y270\u00b0   x -z  y', 'no.12 :  -z0\u00b0   y  x -z', 'no.13 :  -z90\u00b0  -x  y -z', 'no.14 :  -z180\u00b0  -y -x -z', 'no.15 :  -z270\u00b0   x -y -z', 'no.16 :  -x0\u00b0   z  y -x', 'no.17 :  -x90\u00b0  -y  z -x', 'no.18 :  -x180\u00b0  -z -y -x', 'no.19 :  -x270\u00b0   y -z -x', 'no.20 :  -y0\u00b0   x  z -y', 'no.21 :  -y90\u00b0  -z  x -y', 'no.22 :  -y180\u00b0  -x -z -y', 'no.23 :  -y270\u00b0   z -x -y'], 'len' : 0, 'steps' : 1, 'max' : 23, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 1], 'page' : 'gimbalconfig', 'adr' : 51, 'size' : 1, 'unit' : ''},
  'Imu2Orientation' : {'default' : 0, 'name' : 'Imu2 Orientation', 'choices' : ['no.0 :  z0\u00b0   x  y  z', 'no.1 :  z90\u00b0  -y  x  z', 'no.2 :  z180\u00b0  -x -y  z', 'no.3 :  z270\u00b0   y -x  z', 'no.4 :  x0\u00b0   y  z  x', 'no.5 :  x90\u00b0  -z  y  x', 'no.6 :  x180\u00b0  -y -z  x', 'no.7 :  x270\u00b0   z -y  x', 'no.8 :  y0\u00b0   z  x  y', 'no.9 :  y90\u00b0  -x  z  y', 'no.10 :  y180\u00b0  -z -x  y', 'no.11 :  y270\u00b0   x -z  y', 'no.12 :  -z0\u00b0   y  x -z', 'no.13 :  -z90\u00b0  -x  y -z', 'no.14 :  -z180\u00b0  -y -x -z', 'no.15 :  -z270\u00b0   x -y -z', 'no.16 :  -x0\u00b0   z  y -x', 'no.17 :  -x90\u00b0  -y  z -x', 'no.18 :  -x180\u00b0  -z -y -x', 'no.19 :  -x270\u00b0   y -z -x', 'no.20 :  -y0\u00b0   x  z -y', 'no.21 :  -y90\u00b0  -z  x -y', 'no.22 :  -y180\u00b0  -x -z -y', 'no.23 :  -y270\u00b0   z -x -y'], 'len' : 0, 'steps' : 1, 'max' : 23, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 54, 'size' : 1, 'unit' : ''},
  'PitchMotorPoles' : {'default' : 14, 'name' : 'Pitch Motor Poles', 'pos' : [2, 1], 'len' : 0, 'steps' : 2, 'max' : 28, 'type' : 'OPTTYPE_UI', 'min' : 8, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 13, 'size' : 2, 'unit' : ''},
  'PitchMotorDirection' : {'default' : 2, 'name' : 'Pitch Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 14, 'size' : 1, 'unit' : ''},
  'PitchStartupMotorPos' : {'default' : 504, 'name' : 'Pitch Startup Motor Pos', 'len' : 5, 'steps' : 1, 'max' : 1008, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 15, 'size' : 2, 'unit' : ''},
  'FocPitchMotorDirection' : {'default' : 0, 'name' : 'Foc Pitch Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [2, 1], 'page' : 'gimbalconfig', 'adr' : 42, 'size' : 1, 'unit' : ''},
  'FocPitchZeroPos' : {'default' : 0, 'name' : 'Foc Pitch Zero Pos', 'len' : 5, 'steps' : 8, 'max' : 16383, 'type' : 'OPTTYPE_SI', 'min' : -16384, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 43, 'size' : 2, 'unit' : ''},
  'PitchOffset' : {'default' : 0, 'name' : 'Pitch Offset', 'pos' : [2, 4], 'len' : 5, 'steps' : 5, 'max' : 300, 'type' : 'OPTTYPE_SI', 'min' : -300, 'ppos' : 2, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 58, 'size' : 2, 'unit' : '\u00b0'},
  'RollMotorPoles' : {'default' : 14, 'name' : 'Roll Motor Poles', 'pos' : [3, 1], 'len' : 0, 'steps' : 2, 'max' : 28, 'type' : 'OPTTYPE_UI', 'min' : 8, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 16, 'size' : 2, 'unit' : ''},
  'RollMotorDirection' : {'default' : 2, 'name' : 'Roll Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 17, 'size' : 1, 'unit' : ''},
  'RollStartupMotorPos' : {'default' : 504, 'name' : 'Roll Startup Motor Pos', 'len' : 5, 'steps' : 1, 'max' : 1008, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 18, 'size' : 2, 'unit' : ''},
  'FocRollMotorDirection' : {'default' : 0, 'name' : 'Foc Roll Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [3, 1], 'page' : 'gimbalconfig', 'adr' : 44, 'size' : 1, 'unit' : ''},
  'FocRollZeroPos' : {'default' : 0, 'name' : 'Foc Roll Zero Pos', 'len' : 5, 'steps' : 8, 'max' : 16383, 'type' : 'OPTTYPE_SI', 'min' : -16384, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 45, 'size' : 2, 'unit' : ''},
  'RollOffset' : {'default' : 0, 'name' : 'Roll Offset', 'pos' : [3, 4], 'len' : 5, 'steps' : 5, 'max' : 300, 'type' : 'OPTTYPE_SI', 'min' : -300, 'ppos' : 2, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 59, 'size' : 2, 'unit' : '\u00b0'},
  'YawMotorPoles' : {'default' : 14, 'name' : 'Yaw Motor Poles', 'pos' : [4, 1], 'len' : 0, 'steps' : 2, 'max' : 28, 'type' : 'OPTTYPE_UI', 'min' : 8, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 19, 'size' : 2, 'unit' : ''},
  'YawMotorDirection' : {'default' : 2, 'name' : 'Yaw Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 2, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 20, 'size' : 1, 'unit' : ''},
  'YawStartupMotorPos' : {'default' : 504, 'name' : 'Yaw Startup Motor Pos', 'len' : 5, 'steps' : 1, 'max' : 1008, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 21, 'size' : 2, 'unit' : ''},
  'FocYawMotorDirection' : {'default' : 0, 'name' : 'Foc Yaw Motor Direction', 'choices' : ['normal', 'reversed', 'auto'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [4, 1], 'page' : 'gimbalconfig', 'adr' : 46, 'size' : 1, 'unit' : ''},
  'FocYawZeroPos' : {'default' : 0, 'name' : 'Foc Yaw Zero Pos', 'len' : 5, 'steps' : 8, 'max' : 16383, 'type' : 'OPTTYPE_SI', 'min' : -16384, 'ppos' : 0, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 47, 'size' : 2, 'unit' : ''},
  'YawOffset' : {'default' : 0, 'name' : 'Yaw Offset', 'pos' : [4, 4], 'len' : 5, 'steps' : 5, 'max' : 300, 'type' : 'OPTTYPE_SI', 'min' : -300, 'ppos' : 2, 'hidden' : 0, 'page' : 'gimbalconfig', 'adr' : 60, 'size' : 2, 'unit' : '\u00b0'},
  'AccLPF' : {'default' : 2, 'name' : 'Acc LPF', 'choices' : ['off', '1.5 ms', '4.5 ms', '12 ms', '25 ms', '50 ms', '100 ms'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 71, 'size' : 1, 'unit' : ''},
  'RcAdcLPF' : {'default' : 0, 'name' : 'Rc Adc LPF', 'choices' : ['off', '1.5 ms', '4.5 ms', '12 ms', '25 ms', '50 ms', '100 ms'], 'len' : 0, 'steps' : 1, 'max' : 6, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 98, 'size' : 1, 'unit' : ''},
  'HoldToPanTransitionTime' : {'default' : 250, 'name' : 'Hold To Pan Transition Time', 'len' : 5, 'steps' : 25, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 95, 'size' : 2, 'unit' : 'ms'},
  'AccCompensationMethod' : {'default' : 1, 'name' : 'Acc Compensation Method', 'choices' : ['standard', 'advanced'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [1, 6], 'page' : 'expert', 'adr' : 65, 'size' : 1, 'unit' : ''},
  'ImuAccThreshold' : {'default' : 25, 'name' : 'Imu Acc Threshold', 'column' : 2, 'len' : 5, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'expert', 'adr' : 64, 'size' : 2, 'unit' : 'g'},
  'AccNoiseLevel' : {'default' : 40, 'name' : 'Acc Noise Level', 'len' : 0, 'steps' : 1, 'max' : 150, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 3, 'hidden' : 0, 'page' : 'expert', 'adr' : 66, 'size' : 2, 'unit' : 'g'},
  'AccThreshold' : {'default' : 50, 'name' : 'Acc Threshold', 'len' : 0, 'steps' : 1, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 2, 'hidden' : 0, 'page' : 'expert', 'adr' : 67, 'size' : 2, 'unit' : 'g'},
  'AccVerticalWeight' : {'default' : 25, 'name' : 'Acc Vertical Weight', 'len' : 0, 'steps' : 5, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 68, 'size' : 2, 'unit' : '%'},
  'AccZentrifugalCorrection' : {'default' : 30, 'name' : 'Acc Zentrifugal Correction', 'len' : 0, 'steps' : 5, 'max' : 100, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 69, 'size' : 2, 'unit' : '%'},
  'AccRecoverTime' : {'default' : 250, 'name' : 'Acc Recover Time', 'len' : 0, 'steps' : 5, 'max' : 1000, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 70, 'size' : 2, 'unit' : ' ms'},
  'MotorMapping' : {'default' : 0, 'name' : 'Motor Mapping', 'column' : 3, 'choices' : ['M0=pitch , M1=roll', 'M0=roll , M1=pitch', 'roll yaw pitch', 'yaw roll pitch', 'pitch yaw roll', 'yaw pitch roll'], 'len' : 0, 'steps' : 1, 'max' : 5, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 22, 'size' : 1, 'unit' : ''},
  'ImuMapping' : {'default' : 0, 'name' : 'Imu Mapping', 'choices' : ['1 = id1 , 2 = id2', '1 = id2 , 2 = id1'], 'len' : 0, 'steps' : 1, 'max' : 1, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 52, 'size' : 1, 'unit' : ''},
  'ADCCalibration' : {'default' : 1550, 'name' : 'ADC Calibration', 'len' : 0, 'steps' : 10, 'max' : 2000, 'type' : 'OPTTYPE_UI', 'min' : 1000, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 76, 'size' : 2, 'unit' : ''},
  'Imu3Configuration' : {'default' : 0, 'name' : 'Imu3 Configuration', 'column' : 4, 'choices' : ['off', 'default', '2 = id2, 3 = onboard', '2 = onboard, 3 = id2', '2 = onboard, 3 = id3', '2 = onboard, 3 = off'], 'len' : 0, 'steps' : 1, 'max' : 5, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 135, 'size' : 1, 'unit' : ''},
  'Imu3Orientation' : {'default' : 0, 'name' : 'Imu3 Orientation', 'choices' : ['no.0 :  z0\u00b0   x  y  z', 'no.1 :  z90\u00b0  -y  x  z', 'no.2 :  z180\u00b0  -x -y  z', 'no.3 :  z270\u00b0   y -x  z', 'no.4 :  x0\u00b0   y  z  x', 'no.5 :  x90\u00b0  -z  y  x', 'no.6 :  x180\u00b0  -y -z  x', 'no.7 :  x270\u00b0   z -y  x', 'no.8 :  y0\u00b0   z  x  y', 'no.9 :  y90\u00b0  -x  z  y', 'no.10 :  y180\u00b0  -z -x  y', 'no.11 :  y270\u00b0   x -z  y', 'no.12 :  -z0\u00b0   y  x -z', 'no.13 :  -z90\u00b0  -x  y -z', 'no.14 :  -z180\u00b0  -y -x -z', 'no.15 :  -z270\u00b0   x -y -z', 'no.16 :  -x0\u00b0   z  y -x', 'no.17 :  -x90\u00b0  -y  z -x', 'no.18 :  -x180\u00b0  -z -y -x', 'no.19 :  -x270\u00b0   y -z -x', 'no.20 :  -y0\u00b0   x  z -y', 'no.21 :  -y90\u00b0  -z  x -y', 'no.22 :  -y180\u00b0  -x -z -y', 'no.23 :  -y270\u00b0   z -x -y'], 'len' : 0, 'steps' : 1, 'max' : 23, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'expert', 'adr' : 136, 'size' : 1, 'unit' : ''},
  'Uart1Configuration' : {'default' : 0, 'name' : 'Uart1 Configuration', 'choices' : ['off', 'gps target'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [4, 5], 'page' : 'expert', 'adr' : 139, 'size' : 1, 'unit' : ''},
  'MavlinkConfiguration' : {'default' : 0, 'name' : 'Mavlink Configuration', 'choices' : ['no heartbeat', 'emit heartbeat', 'heartbeat + attitude', 'h.b. + mountstatus'], 'len' : 0, 'steps' : 1, 'max' : 3, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'interfaces', 'adr' : 144, 'size' : 1, 'unit' : ''},
  'MavlinkSystemID' : {'default' : 71, 'name' : 'Mavlink System ID', 'len' : 0, 'steps' : 1, 'max' : 255, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'interfaces', 'adr' : 145, 'size' : 2, 'unit' : ''},
  'MavlinkComponentID' : {'default' : 67, 'name' : 'Mavlink Component ID', 'len' : 0, 'steps' : 1, 'max' : 255, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'interfaces', 'adr' : 146, 'size' : 2, 'unit' : ''},
  'UavcanConfiguration' : {'default' : 0, 'name' : 'Uavcan Configuration', 'choices' : ['off', 'normal'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [2, 1], 'page' : 'interfaces', 'adr' : 148, 'size' : 1, 'unit' : ''},
  'UavcanNodeID' : {'default' : 71, 'name' : 'Uavcan Node ID', 'len' : 0, 'steps' : 1, 'max' : 124, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 0, 'hidden' : 0, 'page' : 'interfaces', 'adr' : 149, 'size' : 2, 'unit' : ''},
  'STorM32LinkConfiguration' : {'default' : 0, 'name' : 'STorM32Link Configuration', 'choices' : ['off', 'normal'], 'len' : 0, 'steps' : 1, 'max' : 1, 'hidden' : 0, 'type' : 'OPTTYPE_LISTA', 'min' : 0, 'ppos' : 0, 'pos' : [3, 1], 'page' : 'interfaces', 'adr' : 137, 'size' : 1, 'unit' : ''},
  'STorM32LinkWaitTime' : {'default' : 50, 'name' : 'STorM32Link Wait Time', 'len' : 0, 'steps' : 5, 'max' : 250, 'type' : 'OPTTYPE_UI', 'min' : 0, 'ppos' : 1, 'hidden' : 0, 'page' : 'interfaces', 'adr' : 138, 'size' : 2, 'unit' : 's'},
}

var M =
{
  "Dashboard" :             { 'name' : 'Dashboard', 'page' : 'dashboard' },
  "PID" :                   { 'name' : 'PID', 'page' : 'pid' },
  "Pan" :                   { 'name' : 'Pan', 'page' : 'pan' },
  "RcInputs" :              { 'name' : 'Rc Inputs', 'page' : 'rcinputs' },
  "Functions" :             { 'name' : 'Functions', 'page' : 'functions' },
  "Scripts" :               { 'name' : 'Scripts', 'page' : 'scripts' },
  "Setup" :                 { 'name' : 'Setup', 'page' : 'gimbalsetup' },
  "GimbalConfig" :          { 'name' : 'Gimbal Configuration', 'page' : 'gimbalconfig' },
  "Expert" :                { 'name' : 'Expert', 'page' : 'expert' },
  "Interfaces" :            { 'name' : 'Interfaces', 'page' : 'interfaces' },
  "About" :                 { 'name' : 'About', 'page' : 'about' }
}


function getPstrScale(pstr) {
    var scale = 1.0;  
    var ppos = P[pstr].ppos;
    if( ppos==1 ){ scale *= 0.1; }
    if( ppos==2 ){ scale *= 0.01; }
    if( ppos==3 ){ scale *= 0.001; }
    if( ppos==4 ){ scale *= 0.0001; }
    if( ppos==5 ){ scale *= 0.00001; }
    if( ppos==6 ){ scale *= 0.000001; }
    return scale;
}


function do_crc(buf,len) {
    var buffer = new ArrayBuffer(1024);
    var u8View = new Uint8Array(buffer);
    
    for(var i=0;i<len;i++)
        u8View[i] = parseInt(buf.substr(2*i, 2), 16); //fill typed array buffer from the hex stream
    
    var crc = 0xFFFF;
    for(var i=0;i<len;i++){
        var tmp = u8View[i] ^ (crc & 0xFF );
        tmp = (tmp ^ (tmp<<4)) & 0xFF;
        crc = (crc>>8) ^ (tmp<<8) ^ (tmp<<3) ^ (tmp>>4);
        crc = crc & 0xFFFF;
    }
    
    return crc;
}


//-----------------------------------------------------
// onload initialization
//-----------------------------------------------------

window.onload = function ()
{
    PValues = '';
    PStatus = INVALID;  
    XhttpTransferInProgress = false;
    ConnectionIsValid = false;

    initMenuHtml();
    initAPageHtml();
    initPPageHtml();

    document.getElementById('PDebug').style.display = 'none';
    //document.getElementById('xhttp_responseText').style.display = 'none';
    //document.getElementById('xhttp_allResponseHeaders').style.display = 'none';

    
    var url = document.URL;
    var lastSegment = url.split('/').pop(); //gives the last segment of the url
    updateMenu(null,lastSegment);
    initPBody();
    adaptToFocEnabled();
//    updateRead();

//    document.getElementById('comment').innerText =  "!"+document.body.innerHTML.replace(/</g,'!').replace(/>/g,'!');  
//    document.body.innerHTML =  "<div id='MenuTop' style='display: block; color: #000;  padding: 8px 16px; text-decoration: none;'>!</div>\n"+document.body.innerHTML;  
//    document.body.innerHTML = "<div id='MenuTop'>STorM32 Web App</div>\n" + document.body.innerHTML;  
}


//this are the pages as they also appear in the SETUP_PARAMETERLIST P
// these mirror the first navigation bar (= menu) entries
// it start with the first menu entry, and all menu entries must follow, so that a page also indexes the menu
// the format MUST be as such:
//   "<li><a href='js.html?dashboard' id='MDashboard' onclick='updateMenu(this,\"dashboard\");return false;'>Dashboard</a></li>\n",
// the ?page is used to have a nicier display, but also importantly to figure out the class='active' in the js script
// the last entry is that is also used in SETUP_PARAMTERLIST !!
// js.html is a dummy webpage, for the menu navigation only the ? parameter is used
// this allows to provide a page to cover for the case of an invalid entry
function initMenuHtml() {
    
    var m = "";
    for (var mstr in M) {
       m += "<li><a href='js.html?"+M[mstr].page+"' "+
            "id='M"+mstr+"' onclick='updateMenu(this,\""+M[mstr].page+"\");return false;'>"+M[mstr].name+"</a></li>\n";
    }
    document.getElementById('NavigationBar').innerHTML = m;
    
//    document.getElementById('comment').innerText = m;
}

function initAPageHtml() {
    
    var c = "";
    
    c += "<input id='FileLoadList' type='button' value='Load File List' onclick='fileLoadList()'/>\n";
//    c += "<input id='FileUpLoadDummy' type='button' value='UpLoad File' onclick='fileUpLoadDummy()'/><input id='FileUpLoad' type='file' onchange='fileUpLoad(event)' style='display:none'/>\n"; //it is crucial to do onchange() and not onclick() here!!
//    c += "<input id='FileDownLoad' type='button' value='DownLoad File' onclick='fileDownLoad()'/>\n";
//    c += "<input id='FileDelete' type='button' value='Delete File' onclick='fileDelete()'/>\n";
    c += "<p></p>\n";
    c += "<div class='FileList'><table id='FileList'>\n<tr><th>file</th><th>size</lt></tr>\n</table></div>\n";  
    c += "<div class='FileInfo'>\n";  
    c += "<div class='FileLabel'><label for='FileFreeValue'>free:</label><span id='FileFreeValue'></span></div>";
    c += "<div class='FileLabel'><label for='FileTotalValue'>max:</label><span id='FileTotalValue'></span></div>\n";
    c += "</div>\n";  
    
    document.getElementById('APage').innerHTML += '<p></p>\n\n'+c+'\n';
    
//    document.getElementById('comment').innerText = c;
}




/* the formats must be such:
OPTTYPE_STR+OPTTYPE_READONLY:
<p id='FirmwareVersionField' class='PField' style='display:none'><label for='FirmwareVersion' class='PLabel'>Firmware Version</label>
<input id='FirmwareVersion' class='PInput' type='text' value='' readonly/>
</p>\n

OPTTYPE_LISTA:
<p id='GyroLPFField' class='PField' style='display:none'><label for='GyroLPF' class='PLabel'>Gyro LPF</label>
<select id='GyroLPF' class='PSelect' value='0' onchange='updateListA(\"GyroLPF\")'></select>
</p>\n

OPTTYPE_UI, OPTTYPE_SI:
<p id='PitchPField' class='PField' style='display:none'><label for='PitchP' class='PLabel'>Pitch P</label>
<input id='PitchP' class='PInput' type='number' value='0' onchange='updateUI(\"PitchP\")'/>
<input id='PitchPSlider' class='PSlider' type='range' value='0' onchange='updateUISlider(\"PitchP\")' oninput='updateUISlider(\"PitchP\")'/>
</p>\n
*/
function initPPageHtml() {
    
    var c = "";
    c += "<input id='read' class='read' type='button' value='Read' onclick='updateRead()'/>\n";
    c += "<input id='write' class='write' type='button' value='Write' onclick='updateWrite()'/>\n";
    c += "<input id='storecheck' type='checkbox' name='storecheck' value='dostore' onclick='updateStoreCheck()'/>";
    c += "<p></p>\n";
    document.getElementById('PCmdLine').innerHTML = c;
    
    var p = "";
    for (var pstr in P) {
        switch(P[pstr].type){
        case 'OPTTYPE_STR+OPTTYPE_READONLY':
            p += "<p id='"+pstr+"Field' class='PField' style='display:none'>"+
                 "<label for='"+pstr+"' class='PLabel'>"+P[pstr].name+"</label>"+
                 "<input id='"+pstr+"' class='PInput' type='text' value='' readonly/></p>\n";
            break;
        case 'OPTTYPE_LISTA':    
            p += "<p id='"+pstr+"Field' class='PField' style='display:none'>"+
                 "<label for='"+pstr+"' class='PLabel'>"+P[pstr].name+"</label>"+
                 "<select id='"+pstr+"' class='PSelect' value='0' onchange='updateListA(\""+pstr+"\")'></select></p>\n";
            break;
        case 'OPTTYPE_UI': case 'OPTTYPE_SI':    
            p += "<p id='"+pstr+"Field' class='PField' style='display:none'>"+
                 "<label for='"+pstr+"' class='PLabel'>"+P[pstr].name+"</label>"+
                 "<input id='"+pstr+"' class='PInput' type='number' value='0' onchange='updateUI(\""+pstr+"\")'/>"+
                 "<input id='"+pstr+"Slider' class='PSlider' type='range' value='0' "+
                    "onchange='updateUISlider(\""+pstr+"P\")' oninput='updateUISlider(\""+pstr+"\")'/></p>\n";
            break;
        }
    }
    
    p += "<div id='PDashboardFooter' class='PDashboardFooter'></div>\n";
    
    document.getElementById('PBody').innerHTML = p;    
    
//    document.getElementById('comment').innerText = p;
}

 
function initPBodyListA(pstr) {
    var Elem = document.getElementById(pstr);    

    var html = "";
    for(var i=0; i<P[pstr].choices.length; i++){
        if( i == parseInt(Elem.value) ) {
            html += "<option value='"+i+"' selected>"+P[pstr].choices[i]+"</option>\n";        
        }else{
            html += "<option value='"+i+"'>"+P[pstr].choices[i]+"</option>\n";
        }
    }

    Elem.innerHTML =  html;

    Elem.min = 0;
    Elem.max = parseInt(P[pstr].max); //for a ListA it's an integer
    Elem.value = parseInt(P[pstr].default);
    
//    document.getElementById('comment').innerText = 'initPBodyListA ' + html;
}


function initPBodyUI(pstr) {
    var Elem = document.getElementById(pstr);    

    var scale = getPstrScale(pstr);
  
    var Xmin = parseFloat(P[pstr].min) * scale;
    var Xmax = parseFloat(P[pstr].max) * scale;
    var Xdefault = parseFloat(P[pstr].default) * scale;
    var Xstep = parseFloat(P[pstr].steps) * scale;
  
    Elem.min = Xmin;
    Elem.max = Xmax;
    Elem.step = Xstep;
    Elem.value = Xdefault;
  
    var ElemSlider = document.getElementById(pstr+'Slider');
  
    ElemSlider.min = Xmin; //the order is important, do default last
    ElemSlider.max = Xmax;
    ElemSlider.step = Xstep;
    ElemSlider.value = Xdefault;
  
//    document.getElementById('comment').innerText = 'initPBodyUI ' + Xmin + ',' + Xmax + ',' + Xstep + ',' + scale;
}


function initPDashboardFooter() {
    var c = ''; //'<p></p>\n';
    c += "<div class='DInfo'><span class='DInfoTitle'>Info Center:</span>";
    c += "<div class='DInfoTable'><table>\n";
    c += "<tr><td><label>Imu1</label><span id='DInfoImu1'> -<\span></td><td><label>State</label><span id='DInfoState'> -<\span></td></tr>\n";    
    c += "<tr><td><label>Imu2</label><span id='DInfoImu2'> -<\span></td><td><label>Voltage</label><span id='DInfoVoltage'> -<\span></td></tr>\n";    
    c += "<tr><td><label>Encoders</label><span id='DInfoEncoders'> -<\span></td><td><label>Imu1:</label><span id='DInfoImu1State'> -<\span></td></tr>\n";    
    c += "<tr><td><label>Bat</label><span id='DInfoBat'> -<\span></td><td><label>Imu2:</label><span id='DInfoImu2State'> -<\span></td></tr>\n";    
    c += "<tr><td><label>Motors</label><span id='DInfoMotors'> -<\span></td><td><label>Encoders:</label><span id='DInfoEncodersState'> - - -<\span></td></tr>\n";    
    c += "<tr><td></td><td><label>Bus Errors:</label><span id='DInfoBusErrors'> -<\span></td></tr>\n";    
    c += "</div></table></div>\n";
    
//    document.getElementById('comment').innerText = '\n'+c;
    
    document.getElementById('PDashboardFooter').innerHTML = c;
}


function initPBody() {
    for (var pstr in P) {
        if( !document.getElementById(pstr) ) continue;
        if( P[pstr].type == 'OPTTYPE_LISTA' ) initPBodyListA(pstr);
        if( P[pstr].type == 'OPTTYPE_UI' ) initPBodyUI(pstr);
        if( P[pstr].type == 'OPTTYPE_SI' ) initPBodyUI(pstr);
        if( P[pstr].type == 'OPTTYPE_STR+OPTTYPE_READONLY' ) document.getElementById(pstr).value = '';
    }
    setPAllToInvalid();
    
    initPDashboardFooter();
    
//    document.getElementById('comment').innerText = 'initPBody';
}


//-----------------------------------------------------
// PBody adaption handling
//-----------------------------------------------------

var BoardConfiguration_FOC_DisabledParameters = [
  'Imu2 FeedForward LPF', 'Voltage Correction',
  'Imu2 Configuration', 'Startup Mode',
  'Motor Mapping'
];
var BoardConfiguration_FOC_HidedParameters = [
  'Gyro LPF',
  'Pitch P', 'Pitch I', 'Pitch D', 'Pitch Motor Vmax',
  'Roll P', 'Roll I', 'Roll D', 'Roll Motor Vmax',
  'Yaw P', 'Yaw I', 'Yaw D', 'Yaw Motor Vmax',
  'Pitch Motor Poles', 'Pitch Motor Direction', 'Pitch Startup Motor Pos',
  'Roll Motor Poles', 'Roll Motor Direction', 'Roll Startup Motor Pos',
  'Yaw Motor Poles', 'Yaw Motor Direction', 'Yaw Startup Motor Pos',
];
var BoardConfiguration_FOC_ShownParameters = [
  'Foc Gyro LPF',
  'Foc Pitch P', 'Foc Pitch I', 'Foc Pitch D', 'Foc Pitch K',
  'Foc Roll P', 'Foc Roll I', 'Foc Roll D', 'Foc Roll K',
  'Foc Yaw P', 'Foc Yaw I', 'Foc Yaw D', 'Foc Yaw K',
  'Foc Pitch Motor Direction', 'Foc Pitch Zero Pos',
  'Foc Roll Motor Direction', 'Foc Roll Zero Pos',
  'Foc Yaw Motor Direction', 'Foc Yaw Zero Pos',
];

function arrayContains(array,element)
{
    for(var i=0; i<array.length; i++){ if( array[i] == element ) return true; } //=== type correct comparison
    return false;
}


function i_updateAPage() {
    
}

        
// mstr must be lower case
function i_updatePPage(mstr) {
    if( mstr === 'gimbalsetup' ) mstr = 'setup'; //this is needed since the page name for Setup is different in P and in M
    for (var pstr in P) {
        if( !document.getElementById(pstr) ) continue;
        var disp = 'none';
      
        if( P[pstr].page == mstr ){
            var isFocParam = false;
            if( pstr.match(/Foc/) ) isFocParam = true;
            if( FocIsEnabled ){
                if( arrayContains(BoardConfiguration_FOC_DisabledParameters,P[pstr].name) ){
                     //show disabled //doesn't make sense here since we do not have a grid format of the param fields
                    //disp = 'block'; enable = false;
                }else
                if( arrayContains(BoardConfiguration_FOC_HidedParameters,P[pstr].name) ){
                    //hide
                }else
                if( arrayContains(BoardConfiguration_FOC_ShownParameters,P[pstr].name) ){
                    disp = 'block';
                }else{
                    disp = 'block';
                }
            }else{
                if( !isFocParam ) disp = 'block';
            }
               
        }
          
        document.getElementById(pstr+'Field').style.display = disp;
    }
}


//-----------------------------------------------------
// menu handling
//-----------------------------------------------------

function updateMenu(caller,mstr) {
    mstr = mstr.toLowerCase();
//    document.getElementById('comment').innerText = 'updateMenu '+mstr;  
    document.getElementById('IsLoading').style.display = 'none';
    if( mstr == '' ) mstr = 'dashboard';

    // do the navigation bar
    var lis = document.getElementById('NavigationBar').querySelectorAll('a');
    for(var i=0; i<lis.length; i++){
        var m = lis[i].href.split('?').pop(); 
        if( mstr == m ){ lis[i].classList.add('active'); }else{ lis[i].classList.remove('active'); }
        
//        document.getElementById('comment').innerText += '\n'+i+','+mstr+','+m;
    }  
    
    if( mstr == 'about' ){ //APage
        document.getElementById('APage').style.display = 'block';
        document.getElementById('PPage').style.display = 'none';
        i_updateAPage();
    }else{ //Parameter page  
        document.getElementById('APage').style.display = 'none';
        document.getElementById('PPage').style.display = 'block';
        i_updatePPage(mstr);

        if( mstr == 'dashboard' )
            document.getElementById('PDashboardFooter').style.display = 'block';
        else
            document.getElementById('PDashboardFooter').style.display = 'none';            
    }        
  
    window.scrollTo(0, 0);
    
    return false;
}


//-----------------------------------------------------
// store checkbox handling
//-----------------------------------------------------

function updateStoreCheck() {
    
    if( document.getElementById('storecheck').checked ){
        document.getElementById('write').value = 'Write+Store';
    }else{
        document.getElementById('write').value = 'Write';
    }
}


function setStoreUnchecked() {
    document.getElementById('storecheck').checked = false;
    document.getElementById('write').value = 'Write';
}


function isStoreChecked() {
    return document.getElementById('storecheck').checked;
}


//-----------------------------------------------------
// color handling
//-----------------------------------------------------

function setPColor(pstr,color) {
    var Elem = document.getElementById(pstr);
    if( !Elem ) return;
    Elem.style.backgroundColor = color;
}

function setPToInvalid(pstr){
    setPColor(pstr, '#FFbbbb'); //'red');
    PStatus = INVALID;
}

function setPToValid(pstr) {
    setPColor(pstr, '#bbFFbb'); //'lightgreen');
    PStatus = VALID;
}

function setPToModified(pstr) {
    setPColor(pstr, '#bbbbFF'); //'lightblue');
    PStatus = MODIFIED;
}

function setPAllToInvalid() {
    PValues = '';
    for (var pstr in P) { setPToInvalid(pstr);  }
}

function setPAllToValid() {
    for (var pstr in P) { setPToValid(pstr); }
}


//-----------------------------------------------------
// element update handling
//-----------------------------------------------------

function updateListA(pstr) {
    document.getElementById('comment').innerHTML = 'update'+pstr;
    
    setPToModified(pstr);
}


function parsePFloat(pstr,ppos) {
    var Elem = document.getElementById(pstr);
    var val = parseFloat(Elem.value);
    var min = parseFloat(Elem.min); //can't use P[pstr]. since pstr may have a 'Slider'
    var max = parseFloat(Elem.max); 
    var step = parseFloat(Elem.step); 
    if( val < min ){ val = min; }
    if( val > max ){ val = max; }
    //TODO we here also need to respect the step!!!!

//    document.getElementById('comment').innerHTML='parsePFloat '+pstr+','+ppos+','+min+','+max+','+step+','+val;

    return (val).toFixed(ppos);
}


function updateUI(pstr) {
    document.getElementById('comment').innerHTML = 'update'+pstr;
    var val = parsePFloat(pstr, P[pstr].ppos);
    document.getElementById(pstr).value = val;
    document.getElementById(pstr+'Slider').value = val;
    
    setPToModified(pstr);
}


function updateUISlider(pstr) {
    document.getElementById('comment').innerHTML = 'update'+pstr+'Slider';
    var val = parsePFloat(pstr+'Slider', P[pstr].ppos);
    document.getElementById(pstr).value = val;
    document.getElementById(pstr+'Slider').value = val;
    
    setPToModified(pstr);
}
 

//-----------------------------------------------------
// AJAX
//-----------------------------------------------------

//https://stackoverflow.com/questions/13697829/hexadecimal-to-string-in-javascript
function hex2a(hex) {
    var str = '';
    for (var i = 0; i < hex.length; i += 2) {
        var v = parseInt(hex.substr(i, 2), 16);
        if (v) str += String.fromCharCode(v); //this skips any '\0'
    }
    return str;
} 

//converts a hex XXXX to a u16, taking into account having to swap
function hex2u16(hex) {
    return  parseInt( hex.substr(2,2)+hex.substr(0,2), 16);
} 

//swaps AABB to BBAA
function hexswap(hex) {
    return  hex.substr(2,2)+hex.substr(0,2);
} 

//converts a value into hex XXXX
function a2hex(a) {
    var hex = a.toString(16).toUpperCase();
    while( hex.length < 4 ) hex = '0'+hex;
    return hex;
}  


//converts a u16 into a hex XXXX, taking into account having to swap
function u162hex(a) {
    var hex = a2hex(a);
    return hex.substr(2,2)+hex.substr(0,2);
}    


function setPValueLISTA(pstr,hex) {
    var value = parseInt(hex,16);
    document.getElementById(pstr).value = value;
    setPToValid(pstr);
}    

function setPValueUI(pstr,hex) {
    var scale = getPstrScale(pstr);
    var value = ( parseFloat(parseInt(hex,16)) * scale ).toFixed(P[pstr].ppos);
    document.getElementById(pstr).value = value;
    document.getElementById(pstr+'Slider').value = value;
    setPToValid(pstr);
}    

function setPValueSI(pstr,hex) {
    var scale = getPstrScale(pstr);
    var i = parseInt(hex,16);
    if( i > 32767 ) i -= 65536;
    var value = ( parseFloat(i) * scale ).toFixed(P[pstr].ppos);
    document.getElementById(pstr).value = value;
    document.getElementById(pstr+'Slider').value = value;
    setPToValid(pstr);
}



function adaptToFocEnabled()
{
    //adapt title
    if( FocIsEnabled ){
        document.getElementById('AppConfiguration').innerHTML = " -  for T-STorM32";
    }else{
        document.getElementById('AppConfiguration').innerHTML = " -  for STorM32-NT";
    }
    
    //find active menu
    var mstr = '?';
    var lis = document.getElementById('NavigationBar').querySelectorAll('a');
    for(var i=0; i<lis.length; i++){
        if( lis[i].classList.contains('active') ){ mstr = lis[i].href.split('?').pop(); }
    }  

    //update PBody
    i_updatePPage(mstr);
}


function updateFocEnabled(capabilities)
{
    //check if capability has changed
    var hasFocCapability = false;
    if( capabilities & BOARD_CAPABILITY_FOC ) hasFocCapability = true;
    if( hasFocCapability == FocIsEnabled ) return;
    FocIsEnabled = hasFocCapability;
    
    adaptToFocEnabled();
}


function updateRead()
{
    document.getElementById('comment').innerHTML = 'Read clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';
    ajaxPost('read?p=all', '', function(xhttp){ // ?p=all is ignored currently
        var com = '';
        var args = xhttp.responseText.split(','); //the reponse comes formatted as "v=XX...XX,p=XX...XX,"
        if( (xhttp.responseText.substr(0,1) != 'v')  || (args.length < 2) ){
            ConnectionIsValid = false;
            setPAllToInvalid();
            com = 'failed';
        }else{
            var v = args[0].substr(2);
            var firmware = hex2a(v.substr(0,16*2));
            var board = hex2a(v.substr(16*2,16*2));
            var name = hex2a(v.substr(32*2,16*2));
            var version = hex2u16(v.substr(48*2,2*2));
            var layout = hex2u16(v.substr(50*2,2*2));
            var capabilities = hex2u16(v.substr(52*2,2*2));
        
            updateFocEnabled(capabilities);

            document.getElementById('FirmwareVersion').value = firmware;
            document.getElementById('Board').value = board;
            document.getElementById('Name').value = name;
        
            var g = args[1].substr(2);
            for (var pstr in P) {
                if( !document.getElementById(pstr) ) continue;
                switch( P[pstr].type ){
                    case 'OPTTYPE_LISTA':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueLISTA(pstr,hex);
                        break;
                    case 'OPTTYPE_UI':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueUI(pstr,hex);
                        break;
                    case 'OPTTYPE_SI':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueSI(pstr,hex);
                        break;
                    case 'OPTTYPE_STR+OPTTYPE_READONLY':
                        setPToValid(pstr);
                        break;                
                    default:
                        setPToInvalid(pstr);
                }
            }
            PValues = g;
            PStatus = VALID; //this overrides it
            
            //the connection is valid, so we can trigger updating the status
            updateStatus(); 
        
            com = 'ok' + ','+version+','+layout+','+capabilities+'(x'+a2hex(capabilities)+')'+','+FocIsEnabled;
        }        

        document.getElementById('comment').innerHTML += com;
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
    });
}



function getPValueLISTA(pstr) {
    var value = parseInt(document.getElementById(pstr).value);
    
    setPToValid(pstr);
    return a2hex(value);
}    

function getPValueUI(pstr) {
    var scale = getPstrScale(pstr);
    var value = parseFloat(document.getElementById(pstr).value);
    value = parseInt(Math.round(value / scale));
    if( value < 0 ) value += 65536;
    
    setPToValid(pstr);
    return a2hex(value);
}    

function getPValueSI(pstr) {
    var scale = getPstrScale(pstr);
    var value = parseFloat(document.getElementById(pstr).value);
    value = parseInt(Math.round(value / scale));
    if( value < 0 ) value += 65536;
    
    setPToValid(pstr);
    return a2hex(value);
}    


function setPArray(pa,adr,hex) {
    pa[4*adr] = hex.substr(2,1);
    pa[4*adr+1] = hex.substr(3,1);
    pa[4*adr+2] = hex.substr(0,1);
    pa[4*adr+3] = hex.substr(1,1);
}


function updateWrite()
{
    document.getElementById('comment').innerHTML = 'Write clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';
    
    if( !ConnectionIsValid || (PStatus == INVALID) ){
        document.getElementById('comment').innerHTML += ', no read was done before, hence aborted';
        return;
    }
   
    //take PValues without last 'o' as template, overwrite with those in the Inputs
    var p = PValues.slice(0,-2-4); //remove the last 'o' = '6F' (i.e. two chars) //also remove the crc
    var pa = p.split(''); // array of characters, better to work with than a string
    
    var pp = ''; // this is just for a pretty debug output
    var pa_pretty = pa.slice(); // this is just for a pretty debug output //don't do pa_pretty = p, as this just copies the reference
        
    for (var pstr in P) {
        if( !document.getElementById(pstr) ) continue;
        switch( P[pstr].type ){
            case 'OPTTYPE_LISTA':
                var adr = P[pstr].adr;
                var hex = getPValueLISTA(pstr);
                setPArray(pa, adr, hex);
                
                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'OPTTYPE_UI':
                var adr = P[pstr].adr;
                var hex = getPValueUI(pstr);
                setPArray(pa, adr, hex);

                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'OPTTYPE_SI':
                var adr = P[pstr].adr;
                var hex = getPValueSI(pstr);
                setPArray(pa, adr, hex);

                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'OPTTYPE_STR+OPTTYPE_READONLY': //skip
                break;                
            default: //skip
        }
    }

    p = pa.join(''); //combine it back to a string
    
    var hexcrc = u162hex( do_crc(p, p.length/2) );
    p += hexcrc;
    
    document.getElementById('comment').innerHTML += 'ok' + ',' + hexcrc;//'ok\n' + PValues + '\n' + pa_pretty.join('') + ',' + hexcrc;
    
    var cmd = 'write?p=all';
    if( isStoreChecked() ) cmd = 'write?s=y&p=all';
    
    ConnectionIsValid = true; //set it here, so it can be reset by the xhhtp request
    
    ajaxPost(cmd, p, function(xhttp){ // ?p=all is ignored currently
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
    });
    
    //TODO: we need here to check if the write was successfull!!!
    // both ConnectionIsValid and 'o' must be checked
    
    setPAllToValid();  
    setStoreUnchecked();
}


//-----------------------------------------------------
// status and Info Pane handling
//-----------------------------------------------------

function getStorm32State(state) {
    switch( state ){
        case 0: return 'STARTUP_MOTORS';
        case 1: return 'SETTLE';
        case 2: return 'CALIBRATE';
        case 3: return 'LEVEL';
        case 4: return 'MOTORDIRDETECT';
        case 5: return 'RELEVEL';
        case 6: return 'NORMAL';
        case 7: return 'FASTLEVEL';
        case 32: return 'WAITFORSTORM32LINK';
        case 99: return 'STANDBY';
        case 100: return 'QMODE';
    }
    return 'unknown';
}    

//status flags
var STATUS_IMU_PRESENT =              0x8000; //is checked at start
var STATUS_IMU2_PRESENT =             0x1000; //is checked at start
var STATUS_IMU2_HIGHADR =             0x0800; //is set at start
var STATUS_IMU2_NTBUS =               0x0400; //is set at start

var STATUS_BAT_VOLTAGEISLOW =         0x0010;
var STATUS_BAT_ISCONNECTED =          0x0008; //is set as soon as V>5.5V is detected first time after start
var STATUS_LEVEL_FAILED =             0x0004;

var STATUS_IMU_OK =                   0x0020;
var STATUS_IMU2_OK =                  0x0040;

//status2 flags
var STATUS2_ENCODERS_PRESENT =        0x8000;
var STATUS2_ENCODERYAW_OK =           0x4000;
var STATUS2_ENCODERROLL_OK =          0x2000;
var STATUS2_ENCODERPITCH_OK =         0x1000;

var STATUS2_MOTORYAW_ACTIVE =         0x0020; //sequence is important, must mirror MOTORPITCHENABLED etc., is used by GUI
var STATUS2_MOTORROLL_ACTIVE =        0x0010;
var STATUS2_MOTORPITCH_ACTIVE =       0x0008;


function updateStatus()
{
    if( !ConnectionIsValid ) return;
    
    //document.getElementById('comment').innerHTML = 'Status clicked... ';
    //document.getElementById('xhttp_responseText').innerHTML = '';
    //document.getElementById('xhttp_allResponseHeaders').innerHTML = '';
    ajaxPost('exec?cmd=s', '', function(xhttp){
        var com = '';
        var args = xhttp.responseText; //the reponse comes formatted as "s=XX...XX,"
        if( xhttp.responseText.substr(0,1) != 's' ){
            ConnectionIsValid = false;
            setPAllToInvalid();
            com = 'failed';
        }else{
            var v = args.substr(2); //strip of the 's='
            var state = hex2u16(v.substr(0,2*2));
            var status = hex2u16(v.substr(2*2,2*2));
            var status2 = hex2u16(v.substr(4*2,2*2));
            var status3 = hex2u16(v.substr(6*2,2*2));
            var performance = hex2u16(v.substr(8*2,2*2));
            var errors = hex2u16(v.substr(10*2,2*2));
            var voltage = hex2u16(v.substr(12*2,2*2));
                        
            var c = ''; var c2 = '';

            if( status & STATUS_IMU_PRESENT ){
                c = ' is PRESENT'; c += ' @ NtBus';
                if( status & STATUS_IMU_OK ) c2 = ' OK'; else c2 = ' ERR';
            }else{ 
                c = ' is not available'; c2 = ' -';
            }
            document.getElementById('DInfoImu1').innerHTML = c;
            document.getElementById('DInfoImu1State').innerHTML = c2;
            
            if( status & STATUS_IMU2_PRESENT ){
                c = ' is PRESENT'; 
                if( status & STATUS_IMU2_NTBUS ){ 
                    c += ' @ NtBus';
                }else{
                    if( status & STATUS_IMU2_HIGHADR ){ c+= ' @ high adr = on-board Imu'; }else{ c += ' @ low adr = external Imu'; }
                }
                if( status & STATUS_IMU2_OK ) c2 = ' OK'; else c2 = ' ERR';
            }else{ 
                c = ' is not available'; c2 = ' -';
            }
            document.getElementById('DInfoImu2').innerHTML = c;
            document.getElementById('DInfoImu2State').innerHTML = c2;

            if( status2 & STATUS2_ENCODERS_PRESENT ) c = ' are PRESENT'; else c = ' are not available';
            document.getElementById('DInfoEncoders').innerHTML = c;
            c = '';
            if( status2 & STATUS2_ENCODERS_PRESENT ){
                if( status2 & STATUS2_ENCODERPITCH_OK ) c += ' OK'; else c += ' ERR';
                if( status2 & STATUS2_ENCODERROLL_OK ) c += ' OK'; else c += ' ERR';
                if( status2 & STATUS2_ENCODERYAW_OK ) c += ' OK'; else c += ' ERR';
            }else c += ' - - -'; 
            document.getElementById('DInfoEncodersState').innerHTML = c;
 
            c = ' are';
            if( status2 & STATUS2_MOTORPITCH_ACTIVE ) c += ' ACTIVE'; else c += ' OFF';
            if( status2 & STATUS2_MOTORROLL_ACTIVE ) c += ' ACTIVE'; else c += ' OFF';
            if( status2 & STATUS2_MOTORYAW_ACTIVE ) c += ' ACTIVE'; else c += ' OFF'; 
            document.getElementById('DInfoMotors').innerHTML = c;
                        
            document.getElementById('DInfoState').innerHTML = ' is ' + getStorm32State(state);
            
            if( status & STATUS_BAT_ISCONNECTED ) c = ' is CONNECTED'; else c = ' is not connected';
            document.getElementById('DInfoBat').innerText = c;
            if( status & STATUS_BAT_VOLTAGEISLOW ) c = ' is LOW: '; else c = ' is OK: ';
            document.getElementById('DInfoVoltage').innerText = c + parseFloat(voltage*0.001).toFixed(2)+' V';
           
            document.getElementById('DInfoBusErrors').innerText = parseInt(errors);
       
            com = 'ok';
            
            //connection is valid, so trigger a next time
            setTimeout(updateStatus, 1000);
        }

        //document.getElementById('comment').innerHTML += com;
        //document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        //document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
    });
}



//-----------------------------------------------------
// file handling
//-----------------------------------------------------

function fileLoadList() {
    document.getElementById('comment').innerHTML = 'Load File List clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';

    ajaxPost('fslist?dir=/', 'TEST', function(xhttp){
        //json format { "files" : [ { "name" : "xxxxxx.xxx", "size" : "xxx" } , {} .... ], "total" : "bytes", "free" : "bytes" }
        var c = 'Error in json parse';
        {try{ 
            var Fjson = JSON.parse(xhttp.responseText); 
            c = "<tr><th>file</th><th>size</th></tr>\n";
            for(var i=0; i<Fjson.files.length;i++) {
                c += "<tr><td>"+Fjson.files[i].name+"</td><td>"+Fjson.files[i].size+"</td></tr>\n";
            }
            document.getElementById('FileList').innerHTML = c;
            document.getElementById('FileTotalValue').innerHTML = Fjson.total;
            document.getElementById('FileFreeValue').innerHTML = Fjson.free;
        }catch(e){}}
        
//        document.getElementById('comment').innerText += '\n' + c;
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
    });
}


function fileUpLoadDummy() {
    document.getElementById('FileUpLoad').click();
}

// https://wiki.selfhtml.org/wiki/JavaScript/File_Upload
function fileUpLoad(evt) {
    document.getElementById('comment').innerHTML = 'UpLoad File clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';

    var files = evt.target.files; // FileList object
//    document.getElementById('comment').innerText += '\n' + files + '!' + files.length;
//	for (var i=0; i<files.length; i++) {
//        document.getElementById('comment').innerText += '\n' + files[i].name + '!';
// 	}
    if( !files.length ) return;
    
    var filename = files[0].name;
    document.getElementById('comment').innerText += '\n selected file is ' + filename;
  
    
    
/*
    ajaxPost('fslist?dir=/', 'TEST', function(xhttp){ // ?dir=/ is ignored currently
        //json format [ { "type" : "file" ,"name" : "xxxxxx.xxx", "size" : "xx" } , {} .... ]
        var Fjson = JSON.parse(xhttp.responseText); 
        
        var c = "<tr><th>file</th><th>size</th></tr>\n";
        for(var i=0; i<Fjson.length;i++) {
            c += "<tr><td>"+Fjson[i].name+"</td><td>"+Fjson[i].size+"</td></tr>\n";
        }
        document.getElementById('FileList').innerHTML = c;
        
        document.getElementById('comment').innerText += '\n' + c;
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
    });
*/    
}


function fileDownLoad(evt) {
    document.getElementById('comment').innerHTML = 'DownLoad File clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';
}


function fileDelete() {
    document.getElementById('comment').innerHTML = 'Delete File clicked... ';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';
}