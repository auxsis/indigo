/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.PreviewHelper', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var PreviewGenerator = require('itm_petty_cash.PreviewGenerator');
var PreviewDialog = require('itm_petty_cash.PreviewDialog');


var QWeb = core.qweb;
var _t = core._t;

var PreviewHelper = core.Class.extend({
	createFilePreviewDialog: function(id, widget) {
		widget._rpc({
            fields: ['name', 'mimetype', 'extension','datas'],
            domain: [['id', '=', id]],
            model: 'ir.attachment',
            method: 'search_read',
            limit: 1,
            context: session.user_context,
        }).then(function(files) {
        	var file = files.length > 0 ? files[0] : null;
        	var download_url = '/web/content?' + $.param({
        		model: 'ir.attachment',
    			filename: file.name,
    			filename_field: 'name',
    			field: 'datas',
    			id: file.id,
    			download: true
            });
			PreviewDialog.createPreviewDialog(self, download_url,
				file.mimetype, file.extension, file.name);
		});
	},
	createFilePreviewContent: function(id, widget) {
		return widget._rpc({
	            fields: ['name', 'mimetype', 'extension','datas'],
	            domain: [['id', '=', id]],
	            model: 'ir.attachment',
	            method: 'search_read',
	            limit: 1,
	            context: session.user_context,
	        }).then(function(files) {
	        	var file = files.length > 0 ? files[0] : null;
	        	var download_url = '/web/content?' + $.param({
	        		model: 'ir.attachment',
	    			filename: file.name,
	    			filename_field: 'name',
	    			field: 'datas',
	    			id: file.id,
	    			download: true
	            });
				return PreviewGenerator.createPreview(self, download_url,
					file.mimetype, file.extension, file.name);
			});
	}
});

PreviewHelper.createFilePreviewDialog = function(id, widget) {
    return new PreviewHelper().createFilePreviewDialog(id, widget);
};

PreviewHelper.createFilePreviewContent = function(id, widget) {
    return new PreviewHelper().createFilePreviewContent(id, widget);
};

return PreviewHelper;

});