/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.size', function(require) {
"use strict";

var core = require('web.core');
var registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var field_widgets = require('web.basic_fields');

var _t = core._t;
var QWeb = core.qweb;

function format_size(bytes, field, options) {
    var thresh = options.si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return field_utils.format['float'](bytes, field, options) + ' B';
    }
    var units = options.si
        ? ['KB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return field_utils.format['float'](bytes, field, options) + ' ' + units[u];
}

var FieldDocumentSize = field_widgets.FieldFloat.extend({
	 _renderReadonly: function () {
	    this.$el.text(format_size(this.value, this.field, this.nodeOptions));
    },
});

registry.add('dms_size', FieldDocumentSize);

return FieldDocumentSize;

});
