/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.PreviewWidgets', function (require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var fields = require('web.basic_fields');

var PreviewHandler = require('itm_petty_cash.PreviewHandler');
var PreviewGenerator = require('itm_petty_cash.PreviewGenerator');
var PreviewDialog = require('itm_petty_cash.PreviewDialog');

var QWeb = core.qweb;
var _t = core._t;

fields.FieldBinaryFile.include({
	_renderReadonly: function () {
		this._super();		
		var self = this;
		var $el = this.$el;
		var $wrapper = $('<div/>');
		var $button = $('<button type="button" class="o_binary_preview" aria-hidden="true"/>');
    	$button.append($('<i class="fa fa-file-text-o"></i>'));
    	$button.click(function(e) {
            e.preventDefault();
    		e.stopPropagation();
            var value = self.get('value');
            var filename_fieldname = self.attrs.filename;
            var filename = self.recordData[filename_fieldname] || null;
            PreviewDialog.createPreviewDialog(self, '/web/content?' + $.param({
                'model': self.model,
                'id': self.res_id,
                'field': self.name,
                'filename_field': filename_fieldname,
                'filename': filename,
                'download': true,
                'data': utils.is_bin_size(value) ? null : value,
            }), false, filename ? filename.split('.').pop() : false, filename);
    	});
		$wrapper.addClass($el.attr('class'));
		$el.removeClass("o_field_widget o_hidden");
		this.replaceElement($wrapper);
    	$wrapper.append($button);
    	$wrapper.append($el);
    },
});

});