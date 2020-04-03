/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.binary', function(require) {
"use strict";

var core = require('web.core');
var registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var field_widgets = require('web.basic_fields');

var _t = core._t;
var QWeb = core.qweb;

var FieldDocumentBinary = field_widgets.FieldBinaryFile.extend({
	willStart: function () {
		var self = this;
		return $.when(this._super.apply(this, arguments)).then(function() {
        	return self._rpc({
                model: 'ir.attachment',
                method: 'max_upload_size',        	
                args: [],
            }).then(function(max_upload_size) {
            	var max_upload = parseInt(max_upload_size) || 25;
            	self.max_upload_size = max_upload * 1024 * 1024;
            });
        });
    },
});

registry.add('dms_binary', FieldDocumentBinary);

return FieldDocumentBinary;

});
