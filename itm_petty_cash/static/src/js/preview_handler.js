/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.PreviewHandler', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var QWeb = core.qweb;
var _t = core._t;

var BaseHandler = core.Class.extend({
	init: function(widget) {
		this.widget = widget;
	},
	checkExtension: function(extension) {
		return false;
	},
    checkType: function(mimetype) {
		return false;
	},
    createHtml: function(url, mimetype, extension, title) {
    	return $.when();
    },
});

var PDFHandler = BaseHandler.extend({
	checkExtension: function(extension) {
		return ['.pdf', 'pdf'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/pdf'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();	
    	var viewerUrlTempalte = _.template('/itm_petty_cash/static/lib/PDFjs/web/viewer.html?file=<%= url %>');
		result.resolve($(QWeb.render('ViewerJSFrame', {url: viewerUrlTempalte({url})})));
		return result;
	},    
});

var OpenOfficeHandler = BaseHandler.extend({
	checkExtension: function(extension) {
		return ['.odt', '.odp', '.ods', '.fodt', '.ott', '.fodp', '.otp', '.fods', '.ots',
			'odt', 'odp', 'ods', 'fodt', 'ott', 'fodp', 'otp', 'fods', 'ots'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.presentation',
				'application/vnd.oasis.opendocument.spreadsheet'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();	
    	var viewerUrlTempalte = _.template('/itm_petty_cash/static/lib/ViewerJS/index.html#<%= url %>');
		result.resolve($(QWeb.render('ViewerJSFrame', {url: viewerUrlTempalte({url})})));
		return result;
    },
});

var ImageHandler = BaseHandler.extend({
	cssLibs: [
		'/itm_petty_cash/static/lib/imageviewer/imageviewer.css',
    ],
    jsLibs: [
        '/itm_petty_cash/static/lib/imageviewer/imageviewer.js',
    ],
	checkExtension: function(extension) {
		return ['.cod', '.ras', '.fif', '.gif', '.ief', '.jpeg', '.jpg', '.jpe', '.png', '.tiff',
	        '.tif', '.mcf', '.wbmp', '.fh4', '.fh5', '.fhc', '.ico', '.pnm', '.pbm', '.pgm',
	        '.ppm', '.rgb', '.xwd', '.xbm', '.xpm', 'cod', 'ras', 'fif', 'gif', 'ief', 'jpeg',
	        'jpg', 'jpe', 'png', 'tiff', '.tif', 'mcf', 'wbmp', 'fh4', 'fh5', 'fhc', 'ico',
	        'pnm', 'pbm', 'pgm', '.ppm', 'rgb', 'xwd', 'xbm', 'xpm'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['image/cis-cod', 'image/cmu-raster', 'image/fif', 'image/gif', 'image/ief', 'image/jpeg',
			'image/png', 'image/tiff', 'image/vasa', 'image/vnd.wap.wbmp', 'image/x-freehand', 'image/x-icon',
			'image/x-portable-anymap', 'image/x-portable-bitmap', 'image/x-portable-graymap', 'image/x-portable-pixmap',
			'image/x-rgb', 'image/x-windowdump', 'image/x-xbitmap', 'image/x-xpixmap'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();
    	ajax.loadLibs(this).then(function() {
    		var $content = $(QWeb.render('ImageHTMLContent', {url: url, alt: title}));
    		$content.find('img').click(function (e) {
    			ImageViewer().show(this.src, this.src);
    	    });
            result.resolve($content);
    	});
    	return result;
    },
});


var VideoHandler = BaseHandler.extend({
	mimetypeMap: {
		'.mp4': 'video/mp4',
		'.webm': 'video/webm',
		'.ogg': 'video/ogg',
		'mp4': 'video/mp4',
		'webm': 'video/webm',
		'ogg': 'video/ogg',
	},
	checkExtension: function(extension) {
		return ['.mp4', '.webm', '.ogg', 'mp4', 'webm', 'ogg'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['video/mp4', '	video/webm', 'video/ogg'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();
    	if(!mimetype || mimetype === 'application/octet-stream') {
    		mimetype = this.mimetypeMap[extension];
    	}
		var $content = $(QWeb.render('VideoHTMLContent', {url: url, type: mimetype}));
        result.resolve($content);
		return $.when(result);
    },
});

var WordHandler = PDFHandler.extend({
	checkExtension: function(extension) {
		return ['.doc', '.docx', '.docm', 'doc', 'docx', 'docm'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/msword', 'application/ms-word', 'application/vnd.ms-word.document.macroEnabled.12',
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var convertUrlTempalte = _.template('/web/preview/msoffice?url=<%= url %>');
    	return this._super(convertUrlTempalte({url: encodeURIComponent(url)}));
    },
});

var PowerPointHandler = PDFHandler.extend({
	checkExtension: function(extension) {
		return ['.ppt', '.pptx', '.pptm', 'ppt', 'pptx', 'pptm'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/vnd.mspowerpoint', 'application/vnd.ms-powerpoint',
			'application/vnd.openxmlformats-officedocument.presentationml.presentation',
			'application/vnd.ms-powerpoint.presentation.macroEnabled.12'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var convertUrlTempalte = _.template('/web/preview/msoffice?url=<%= url %>');
    	return this._super(convertUrlTempalte({url: encodeURIComponent(url)}));
    },
});

var ExcelHandler = BaseHandler.extend({
	cssLibs: [
		'/itm_petty_cash/static/lib/handsontable/handsontable.css',
    ],
    jsLibs: [
        '/itm_petty_cash/static/lib/jQueryBinaryTransport/jquery-binarytransport.js',
        '/itm_petty_cash/static/lib/SheetJS/xlsx.js',
        '/itm_petty_cash/static/lib/handsontable/handsontable.js'
    ],
	checkExtension: function(extension) {
		return ['.xls', '.xlsx', '.xlsm', '.xlsb', 'xls', 'xlsx', 'xlsm', 'xlsb'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/vnd.ms-excel', 'application/vnd.msexcel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/vnd.ms-excel.sheet.binary.macroEnabled.12', 'application/vnd.ms-excel.sheet.macroEnabled.12'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();
    	var $content = $(QWeb.render('ExcelHTMLContent'));
    	ajax.loadLibs(this).then(function() {
	    	$.ajax(url, {
				type: "GET",
				dataType: "binary",
				responseType:'arraybuffer',
				processData: false,
				success: function(arraybuffer) {
					var data = new Uint8Array(arraybuffer);
					var arr = new Array();
					for(var i = 0; i != data.length; ++i) {
						arr[i] = String.fromCharCode(data[i]);
					}
					var workbook = XLSX.read(arr.join(""), {
						type:"binary",
						cellDates:true,
						cellStyles:true,
						cellNF:true
					});
					var jsonWorkbook = {};
					_.each(workbook.SheetNames, function(sheet, index, list) {
						var jsonData = XLSX.utils.sheet_to_json(workbook.Sheets[sheet], {header:1});
						if(jsonData.length > 0) {
							jsonWorkbook[sheet] = jsonData;
						}
						var worksheet = workbook.Sheets[sheet];
					});
					$content.find('.excel-loader').hide();
					$content.find('.excel-container').show();
					var index = 0;
					_.each(jsonWorkbook, function(sheet, sheetname, list) {
						var $tab = $('<a/>');
						$tab.attr('href', '#sheet-' + index);
		    			$tab.attr('aria-controls', 'sheet-' + index);
		    			$tab.attr('role', 'tab');
		    			$tab.attr('data-toggle', 'tab');
		    			$tab.append('<i class="fa fa-table" aria-hidden="true"></i>');
		    			$tab.append($('<span/>').text(sheetname));
			    		$content.find('.nav-tabs').append($('<li/>').append($tab));
		    			var $pane = $('<div/>');
		    			$pane.addClass('tab-pane table-container');
		    			$pane.attr('id', 'sheet-' + index);
		    			$pane.handsontable({
						    data: sheet,
						    rowHeaders: true,
						    colHeaders: true,
						    stretchH: 'all',
						    readOnly: true,
						    columnSorting: true,
						    autoColumnSize: true,
		    			});
		    			$content.find('.tab-content').append($pane);
		    			if(index == 0) {
		    				$tab.tab('show');
		    			}
		    			index++;
					});
				},
				error: function(request, status, error) {
			    	console.error(request.responseText);
			    },
			});
    	});
        result.resolve($content);
		return result;
    },
});


return {
	BaseHandler: BaseHandler,
	PDFHandler: PDFHandler,
	OpenOfficeHandler: OpenOfficeHandler,
	ImageHandler: ImageHandler,
	VideoHandler: VideoHandler,
	ExcelHandler: ExcelHandler,
	WordHandler: WordHandler,
	PowerPointHandler: PowerPointHandler,
};

});