/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.utils', function (require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');

var mapping = [
	['file-image-o', /^image\//],
	['file-audio-o', /^audio\//],
	['file-video-o', /^video\//],
	['file-pdf-o', 'application/pdf'],
	['file-text-o', 'text/plain'],
	['file-code-o', [
		'text/html',
	    'text/javascript',
		'application/javascript' 
	]],
	['file-archive-o', [
	    /^application\/x-(g?tar|xz|compress|bzip2|g?zip)$/,
	    /^application\/x-(7z|rar|zip)-compressed$/,
	    /^application\/(zip|gzip|tar)$/
	]],
	['file-word-o', [ 
        /ms-?word/, 'application/vnd.oasis.opendocument.text',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]],
	['file-powerpoint-o', [
	    /ms-?powerpoint/,
		'application/vnd.openxmlformats-officedocument.presentationml.presentation'
	]],
	['file-excel-o', [ 
	    /ms-?excel/,
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	]],
	['file-o' ]
]

function match(mimetype, cond) {
	if (Array.isArray(cond)) {
		return cond.reduce(function(v, c) {
			return v || match(mimetype, c)
		}, false)
	} else if (cond instanceof RegExp) {
		return cond.test(mimetype)
	} else if (cond === undefined) {
		return true
	} else {
		return mimetype === cond
	}
}

var cache = {}
function resolve(mimetype) {
	if (cache[mimetype]) {
		return cache[mimetype]
	}
	for (var i = 0; i < mapping.length; i++) {
		if (match(mimetype, mapping[i][1])) {
			cache[mimetype] = mapping[i][0]
			return mapping[i][0]
		}
	}
}

function mimetype2fa(mimetype, options) {
	if (typeof mimetype === 'object') {
		options = mimetype
		return function(mimetype) {
			return mimetype2fa(mimetype, options)
		}
	} else {
		var icon = resolve(mimetype)
		if (icon && options && options.prefix) {
			return options.prefix + icon
		} else {
			return icon
		}
	}
}

function format_number(value) {
	if (value === false) {
	    return "";
	}
	var l10n = core._t.database.parameters;
	var formatted = _.str.sprintf('%.' + 2 + 'f', value || 0).split('.');
	formatted[0] = utils.insert_thousand_seps(formatted[0]);
	return formatted.join(l10n.decimal_point);
}

function format_size(bytes) {
    if(Math.abs(bytes) < 1000) {
        return format_number(bytes) + ' B';
    }
    var units = ['KB','MB','GB','TB','PB','EB','ZB','YB'];
    var u = -1;
    do {
        bytes /= 1000;
        ++u;
    } while(Math.abs(bytes) >= 1000 && u < units.length - 1);
    return format_number(bytes) + ' ' + units[u];
}

var delay = (function(){
    var timer = 0;
    return function(callback, ms){
    	clearTimeout (timer);
    	timer = setTimeout(callback, ms);
    };
})();

return {
	mimetype2fa: mimetype2fa,
	format_size: format_size,
	delay: delay,
}

});
