'use strict';

/*TODO:
- always do a read before a write ?
- check validity after a write


*/

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

//this is flag tells if the ESP is in AP+Gopro Station mode
var GoproIsAvailable = false;

//this is the string of hex received via read, i.e. g
// it is needed to keep the scripts, and to keep values not available or changed
// it has to be maintained
var PValues = '';

//this is to maintain the status of the PValues
var INVALID = 0;
var VALID = 1;
var MODIFIED = 2;
var PStatus = INVALID;  //this can be invalid = 0, valid = 1, modified; 

//var P is in extern .js

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
  "Interfaces" :            { 'name' : 'Interfaces', 'page' : 'interfaces' },
  "Expert" :                { 'name' : 'Expert', 'page' : 'expert' },
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
    GoproIsAvailable = false;

    if( document.getElementById('GoproPage') && (document.getElementById('GoproPage').style.display != 'none') )
        GoproIsAvailable = true;
        
    initMenuHtml();
    initAPageHtml();
    initGoproPageHtml();
    initPPageHtml();

    //document.getElementById('PDebug').style.display = 'block';
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
    if( GoproIsAvailable )
       m += "<li><a href='js.html?gopro' "+
            "id='MGopro' onclick='updateMenu(this,\"gopro\");return false;'>GoPro Hero5</a></li>\n";
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


function initGoproPageHtml() {

    if( !GoproIsAvailable ) return;
    
    var c = "";
    c += "<input id='GoproShutterOn' type='button' value='Shutter On' onclick='updateGoproShutterOn()'/>\n";
    c += "<input id='GoproShutterOff' type='button' value='Shutter Off' onclick='updateGoproShutterOff()'/>\n";
    c += "<p></p>\n";
    c += "<input id='GoproPowerOff' type='button' value='Power Off' onclick='updateGoproPowerOff()'/>\n";
    
    document.getElementById('GoproPage').innerHTML = c;
    
//    document.getElementById('comment').innerText = c;
}



/* the formats must be such:
STR+READONLY:
<p id='FirmwareVersionField' class='PField' style='display:none'><label for='FirmwareVersion' class='PLabel'>Firmware Version</label>
<input id='FirmwareVersion' class='PInput' type='text' value='' readonly/>
</p>\n

LIST:
<p id='GyroLPFField' class='PField' style='display:none'><label for='GyroLPF' class='PLabel'>Gyro LPF</label>
<select id='GyroLPF' class='PSelect' value='0' onchange='updateListA(\"GyroLPF\")'></select>
</p>\n

UINT, INT:
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
        case 'STR+READONLY':
            p += "<p id='"+pstr+"Field' class='PField' style='display:none'>"+
                 "<label for='"+pstr+"' class='PLabel'>"+P[pstr].name+"</label>"+
                 "<input id='"+pstr+"' class='PInput' type='text' value='' readonly/></p>\n";
            break;
        case 'LIST':    
            p += "<p id='"+pstr+"Field' class='PField' style='display:none'>"+
                 "<label for='"+pstr+"' class='PLabel'>"+P[pstr].name+"</label>"+
                 "<select id='"+pstr+"' class='PSelect' value='0' onchange='updateListA(\""+pstr+"\")'></select></p>\n";
            break;
        case 'UINT': case 'INT':    
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
    c += "<tr><td><label>STorM32-Link</label><span id='DInfoSTorM32Link'> -<\span></td><td><label>Imu2:</label><span id='DInfoImu2State'> -<\span></td></tr>\n";    
    c += "<tr><td><label>Bat</label><span id='DInfoBat'> -<\span></td><td><label>Encoders:</label><span id='DInfoEncodersState'> - - -<\span></td></tr>\n";    
    c += "<tr><td><label>Motors</label><span id='DInfoMotors'> -<\span></td><td><label>Bus Errors:</label><span id='DInfoBusErrors'> -<\span></td></tr>\n";    
    c += "</div></table></div>\n";
    
//    document.getElementById('comment').innerText = '\n'+c;
    
    document.getElementById('PDashboardFooter').innerHTML = c;
}


function initPBody() {
    for (var pstr in P) {
        if( !document.getElementById(pstr) ) continue;
        if( P[pstr].type == 'LIST' ) initPBodyListA(pstr);
        if( P[pstr].type == 'UINT' ) initPBodyUI(pstr);
        if( P[pstr].type == 'INT' ) initPBodyUI(pstr);
        if( P[pstr].type == 'STR+READONLY' ) document.getElementById(pstr).value = '';
    }
    
    initPDashboardFooter();
    
    setPAllToInvalid();
    
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


function i_updateGoproPage() {
    
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
        document.getElementById('GoproPage').style.display = 'none';
        document.getElementById('PPage').style.display = 'none';
        i_updateAPage();
    }else
    if( (mstr == 'gopro') && GoproIsAvailable ){ //GoproPage
        document.getElementById('APage').style.display = 'none';
        document.getElementById('GoproPage').style.display = 'block';
        document.getElementById('PPage').style.display = 'none';
        i_updateGoproPage();
    }else{ //Parameter page  
        document.getElementById('APage').style.display = 'none';
        document.getElementById('GoproPage').style.display = 'none';
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
    clearStatus();
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
            alert("Read failed, no connection to STorM32.");
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
                    case 'LIST':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueLISTA(pstr,hex);
                        break;
                    case 'UINT':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueUI(pstr,hex);
                        break;
                    case 'INT':
                        var adr = P[pstr].adr;
                        var hex = g.substr(4*adr+2,2)+g.substr(4*adr,2);
                        setPValueSI(pstr,hex);
                        break;
                    case 'STR+READONLY':
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
            case 'LIST':
                var adr = P[pstr].adr;
                var hex = getPValueLISTA(pstr);
                setPArray(pa, adr, hex);
                
                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'UINT':
                var adr = P[pstr].adr;
                var hex = getPValueUI(pstr);
                setPArray(pa, adr, hex);

                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'INT':
                var adr = P[pstr].adr;
                var hex = getPValueSI(pstr);
                setPArray(pa, adr, hex);

                pp += hex + '('+ parseInt(adr) + '=' + parseInt(hex,16) +'),';
                setPArray(pa_pretty, adr, hex);
                pa_pretty[4*adr] = '<span style="color:red">'+pa_pretty[4*adr]; pa_pretty[4*adr+3] += '</span>';
                break;
            case 'STR+READONLY': //skip
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
        case 99: return 'STANDBY';
        case 100: return 'QMODE';
    }
    return 'unknown';
}    

//status flags
var STATUS_IMU_PRESENT =              0x8000; //is checked at start
var STATUS_IMU_OK =                   0x0020;
var STATUS_IMU2_PRESENT =             0x1000; //is checked at start
var STATUS_IMU2_HIGHADR =             0x0800; //is set at start
var STATUS_IMU2_NTBUS =               0x0400; //is set at start
var STATUS_IMU2_OK =                  0x0040;

var STATUS_BAT_VOLTAGEISLOW =         0x0010;
var STATUS_BAT_ISCONNECTED =          0x0008; //is set as soon as V>5.5V is detected first time after start
var STATUS_LEVEL_FAILED =             0x0004;

var STATUS_STORM32LINK_PRESENT =      0x0100;
var STATUS_STORM32LINK_OK =           0x0002;
var STATUS_STORM32LINK_INUSE =        0x0001; //is set permanently once it was once OK

var STATUS_EMERGENCY =                0x0080

//status2 flags
var STATUS2_ENCODERS_PRESENT =        0x8000;
var STATUS2_ENCODERYAW_OK =           0x4000;
var STATUS2_ENCODERROLL_OK =          0x2000;
var STATUS2_ENCODERPITCH_OK =         0x1000;

var STATUS2_MOTORYAW_ACTIVE =         0x0020; //sequence is important, must mirror MOTORPITCHENABLED etc., is used by GUI
var STATUS2_MOTORROLL_ACTIVE =        0x0010;
var STATUS2_MOTORPITCH_ACTIVE =       0x0008;


function clearStatus()
{
    document.getElementById('DInfoImu1').innerHTML = '-';
    document.getElementById('DInfoImu1State').innerHTML = '-';
    document.getElementById('DInfoImu2').innerHTML = '-';
    document.getElementById('DInfoImu2State').innerHTML = '-';
    document.getElementById('DInfoEncoders').innerHTML = '-';
    document.getElementById('DInfoEncodersState').innerHTML = '- - -';
    document.getElementById('DInfoMotors').innerHTML = '-';
    document.getElementById('DInfoState').innerHTML = '-';
    document.getElementById('DInfoBat').innerText = '-';
    document.getElementById('DInfoSTorM32Link').innerText = '-';
    document.getElementById('DInfoVoltage').innerText = '-';
    document.getElementById('DInfoBusErrors').innerText = '-';
}


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
 
            if( status & STATUS_STORM32LINK_PRESENT ){
                if( status & STATUS_STORM32LINK_INUSE ) c = ' is INUSE'; else c = ' is PRESENT';
            }else c = ' is not available';
            document.getElementById('DInfoSTorM32Link').innerHTML = c;
    
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








//-----------------------------------------------------
// GoPro handling
//-----------------------------------------------------
//we don't need to check for GoproIsAvailable here
// the commands are supported, they will return an 'e' if no Gopro is connected 

function updateGoproShutterOn()
{
    document.getElementById('comment').innerHTML = 'Shutter On clicked';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';

    ajaxPost('gps1', '', function(xhttp){
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
        
        if( xhttp.responseText == 'e' ) alert("No connection to Gopro.");
    });
}

function updateGoproShutterOff()
{
    document.getElementById('comment').innerHTML = 'Shutter Off clicked';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';

    ajaxPost('gps0', '', function(xhttp){
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
        
        if( xhttp.responseText == 'e' ) alert("No connection to Gopro.");
    });
}

function updateGoproPowerOff()
{
    document.getElementById('comment').innerHTML = 'Power Off clicked';
    document.getElementById('xhttp_responseText').innerHTML = '';
    document.getElementById('xhttp_allResponseHeaders').innerHTML = '';

    ajaxPost('gpp0', '', function(xhttp){
        document.getElementById('xhttp_responseText').innerHTML = xhttp.responseText;
        document.getElementById('xhttp_allResponseHeaders').innerHTML = xhttp.getAllResponseHeaders();
        
        if( xhttp.responseText == 'e' ) alert("No connection to Gopro.");
    });
}
