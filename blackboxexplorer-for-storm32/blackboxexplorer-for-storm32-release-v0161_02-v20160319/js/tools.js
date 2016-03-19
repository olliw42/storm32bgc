"use strict";

//Convert a hexadecimal string (that represents a binary 32-bit float) into a float
function hexToFloat(string) {
    var arr = new Uint32Array(1);
    arr[0] = parseInt(string, 16);
    
    var floatArr = new Float32Array(arr.buffer);
    
    return floatArr[0]; 
}

function uint32ToFloat(value) {
    var arr = new Uint32Array(1);
    arr[0] = value;
    
    var floatArr = new Float32Array(arr.buffer);

    return floatArr[0]; 
}

function asciiArrayToString(arr) {
    return String.fromCharCode.apply(null, arr);
}

function asciiStringToByteArray(s) {
    var bytes = [];
    
    for (var i = 0; i < s.length; i++)
        bytes.push(s.charCodeAt(i));
    
    return bytes;
}

function signExtend24Bit(u) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (u & 0x800000) ? (u | 0xFF000000) : u;
}

function signExtend16Bit(word) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (word & 0x8000) ? (word | 0xFFFF0000) : word;
}

function signExtend14Bit(word) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (word & 0x2000) ? (word | 0xFFFFC000) : word;
}

function signExtend8Bit(byte) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (byte & 0x80) ? (byte | 0xFFFFFF00) : byte;
}

function signExtend6Bit(byte) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (byte & 0x20) ? (byte | 0xFFFFFFC0) : byte;
}

function signExtend4Bit(nibble) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (nibble & 0x08) ? (nibble | 0xFFFFFFF0) : nibble;
}

function signExtend2Bit(byte) {
    //If sign bit is set, fill the top bits with 1s to sign-extend
    return (byte & 0x02) ? (byte | 0xFFFFFFFC) : byte;
}

/**
 * Get the first index of needle in haystack, or -1 if it was not found. Needle and haystack
 * are both byte arrays.
 * 
 * Provide startIndex in order to specify the first index to search from
 * @param haystack
 * @param needle
 * @returns {Number}
 */
function memmem(haystack, needle, startIndex) {
    var i, j, found;
    
    for (var i = startIndex ? startIndex : 0; i <= haystack.length - needle.length; i++) {
        if (haystack[i] == needle[0]) {
            for (var j = 1; j < needle.length && haystack[i + j] == needle[j]; j++)
                ;
        
            if (j == needle.length)
                return i;
        }
    }
    
    return -1;
}

function parseCommaSeparatedIntegers(string) {
    var 
        parts = string.split(","),
        result = new Array(parts.length);
    
    for (var i = 0; i < parts.length; i++) {
        result[i] = parseInt(parts[i], 10);
    }

    return result;
}

/**
 * Find the index of `item` in `list`, or if `item` is not contained in `list` then return the index
 * of the next-smaller element (or 0 if `item` is smaller than all values in `list`).
 */
function binarySearchOrPrevious(list, item) {
    var
        min = 0,
        max = list.length,
        mid, 
        result = 0;
    
    while (min < max) {
        mid = Math.floor((min + max) / 2);
        
        if (list[mid] === item)
            return mid;
        else if (list[mid] < item) {
            // This might be the largest element smaller than item, but we have to continue the search right to find out
            result = mid;
            min = mid + 1;
        } else
            max = mid;
    }
    
    return result;
}

/**
 * Find the index of `item` in `list`, or if `item` is not contained in `list` then return the index
 * of the next-larger element (or the index of the last item if `item` is larger than all values in `list`).
 */
function binarySearchOrNext(list, item) {
    var
        min = 0,
        max = list.length,
        mid, 
        result = list.length - 1;
    
    while (min < max) {
        mid = Math.floor((min + max) / 2);
        
        if (list[mid] === item)
            return mid;
        else if (list[mid] > item) {
            // This might be the smallest element larger than item, but we have to continue the search left to find out
            max = mid;
            result = mid;
        } else
            min = mid + 1;
    }
    
    return result;
}

function leftPad(string, pad, minLength) {
    string = "" + string;
    
    while (string.length < minLength)
        string = pad + string;
    
    return string;
}

function formatTime(msec, displayMsec) {
    var
        secs, mins, hours;
    
    msec = Math.round(msec);
    
    secs = Math.floor(msec / 1000);
    msec %= 1000;

    mins = Math.floor(secs / 60);
    secs %= 60;

    hours = Math.floor(mins / 60);  
    mins %= 60;
    
    return (hours ? leftPad(hours, "0", 2) + ":" : "") + leftPad(mins, "0", 2) + ":" + leftPad(secs, "0", 2)
        + (displayMsec ? "." + leftPad(msec, "0", 3) : "");
}