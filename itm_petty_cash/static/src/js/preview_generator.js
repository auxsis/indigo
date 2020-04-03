/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.PreviewGenerator', function (require) {
"use strict";

var core = require('web.core');

var PreviewHandler = require('itm_petty_cash.PreviewHandler');

var QWeb = core.qweb;
var _t = core._t;

var PreviewGenerator = core.Class.extend({
	handler: {},
	init: function(widget, additional_handler) {
		this.widget = widget;
		this.handler = _.extend(this.handler, {
			"PDFHandler": new PreviewHandler.PDFHandler(widget),
			"OpenOfficeHandler": new PreviewHandler.OpenOfficeHandler(widget),
			"ImageHandler": new PreviewHandler.ImageHandler(widget),
			"VideoHandler": new PreviewHandler.VideoHandler(widget),
			"ExcelHandler": new PreviewHandler.ExcelHandler(widget),
			"WordHandler": new PreviewHandler.WordHandler(widget),
			"PowerPointHandler": new PreviewHandler.PowerPointHandler(widget),
		});
		this.handler = _.extend(this.handler, additional_handler);
	},
	createPreview: function(url, mimetype, extension, title) {
		var matchedHandler = false;
		_.each(this.handler, function(handler, key, handler_list) {
			if(handler.checkExtension(extension) || handler.checkType(mimetype)) {
				matchedHandler = handler;
			}
		});
		if(matchedHandler) {
			return matchedHandler.createHtml(url, mimetype, extension, title);
		} else {
			var $content = $.Deferred();
			$content.resolve($(QWeb.render('UnsupportedContent', {
				url: url, mimetype: mimetype || _t('Unknown'),
				extension: extension || _t('Unknown'),
				title: title || _t('Unknown')
			})));
			return $content;
		}
	}
});

PreviewGenerator.createPreview = function(widget, url, mimetype, extension, title) {
    return new PreviewGenerator(widget, {}).createPreview(url, mimetype, extension, title);
};

return PreviewGenerator;

});