/* jquery-debug.js -- debug logging for jquery+firebug
 * 
 * Safe logging to firebug in Firefox.
 * 
 * http://happygiraffe.net/blog/2007/09/26/jquery-logging/
 * http://code.google.com/p/fbug/source/browse/branches/firebug1.2/lite/firebugx.js?r=187
 * 
 */
if (!window.console || !console.firebug) {
    // Set up a fake console to accept log messages.
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir", 
		 "dirxml", "group", "groupEnd", "time", "timeEnd", "count", 
		 "trace", "profile", "profileEnd"];

    window.console = {};
    for (var i = 0; i < names.length; ++i)
        window.console[names[i]] = function() {};

}

jQuery.fn.log = function (msg) {
    console.log("%s: %o", msg, this);
    return this;
};    

