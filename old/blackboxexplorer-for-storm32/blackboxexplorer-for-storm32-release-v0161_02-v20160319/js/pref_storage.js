"use strict";

/**
 * A local key/value store for JSON-encodable values. Supports localStorage and chrome.storage.local backends.
 * 
 * Supply keyPrefix if you want it automatically prepended to key names.
 */
function PrefStorage(keyPrefix) {
    var
        LOCALSTORAGE = 0,
        CHROME_STORAGE_LOCAL = 1,
    
        mode;
    
    /**
     * Fetch the value with the given name, calling the onGet handler (possibly asynchronously) with the retrieved
     * value, or null if the value didn't exist.
     */
    this.get = function(name, onGet) {
        name = keyPrefix + name;
        
        switch (mode) {
            case LOCALSTORAGE:
                var
                    parsed = null;
                
                try {
                    parsed = JSON.parse(window.localStorage[name]); 
                } catch (e) {
                }
                
                onGet(parsed);
            break;
            case CHROME_STORAGE_LOCAL:
                chrome.storage.local.get(name, function(data) {
                    onGet(data[name]);
                });
            break;
        }
    };
    
    /**
     * Set the given JSON-encodable value into storage using the given name.
     */
    this.set = function(name, value) {
        name = keyPrefix + name;

        switch (mode) {
            case LOCALSTORAGE:
                window.localStorage[name] = JSON.stringify(value);
            break;
            case CHROME_STORAGE_LOCAL:
                var
                    data = {};
                
                data[name] = value;
                
                chrome.storage.local.set(data);
            break;
        }
    };
    
    if (window.chrome && window.chrome.storage && window.chrome.storage.local) {
        mode = CHROME_STORAGE_LOCAL;
    } else {
        mode = LOCALSTORAGE;
    }
    
    keyPrefix = keyPrefix || "";
}