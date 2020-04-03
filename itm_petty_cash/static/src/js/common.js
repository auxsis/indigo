/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.common', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var utils = require('web.utils');

var QWeb = core.qweb;
var _t = core._t;

var delay = (function(){
    var timer = 0;
    return function(callback, ms){
    	clearTimeout (timer);
    	timer = setTimeout(callback, ms);
    };
})();

function format_number(value) {
	if (value === false || typeof value !== "number") {
	    return "";
	}
	var l10n = core._t.database.parameters;
	var formatted = _.str.sprintf('%.' + 2 + 'f', value || 0).split('.');
	formatted[0] = utils.insert_thousand_seps(formatted[0]);
	return formatted.join(l10n.decimal_point);
}

function format_size(bytes, options) {
	var options = options || {};
    var thresh = options.si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
    	return format_number(bytes) + ' B';
    }
    var units = options.si
        ? ['KB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return format_number(bytes) + ' ' + units[u];
}


function unique_string() {
    function chr4() {
        return Math.random().toString(16).slice(-4);
    }
    return chr4() + chr4() + '-' + chr4() + '-' + chr4() + '-' + chr4() + '-' + chr4() + chr4() + chr4();
}

function unique_id(prefix) {
	var random = unique_string();
	var prefix = prefix || "";
	var id = prefix + random;
	while ($('#' + id).length >= 1) {
        id = prefix + unique_string();
    }
   	return id;
}

return {
	delay: delay,
	format_number: format_number,
	format_size: format_size,
	unique_string: unique_string,
	unique_id: unique_id,
};

});