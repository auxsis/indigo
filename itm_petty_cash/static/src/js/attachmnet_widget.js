/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.attachmnet_widget', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var framework = require('web.framework');
var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var ajax = require('web.ajax');
var config = require('web.config');
var session = require('web.session');
var web_client = require('web.web_client');
var crash_manager = require('web.crash_manager');

var dms_utils = require('itm_petty_cash.utils');

var ControlPanelMixin = require('web.ControlPanelMixin');
var PreviewHelper = require('itm_petty_cash.PreviewHelper');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');

var _t = core._t;
var QWeb = core.qweb;


var ShowAttachmnetWidget = AbstractField.extend({
	cssLibs: [
        '/itm_petty_cash/static/lib/jquery-splitter/css/jquery.splitter.css',
        '/itm_petty_cash/static/lib/jsTree/themes/proton/style.css',
    ],
    jsLibs: [
        '/itm_petty_cash/static/lib/jquery-splitter/js/jquery.splitter.js',
        '/itm_petty_cash/static/lib/jsTree/jstree.js',
    ],
	template: 'itm_petty_cash.AttachmnetTreeViews',
	start: function() {
        var self = this;
        return this._super().then(function() {
            self.render();
        });
    },
    _load_data: function() {
    	var self = this;
    	var data_loaded = $.Deferred();
    	var data_parts = [];
    	var info = JSON.parse(this.value);
		var line_id = info.line_id
		var title = info.title
		var attachment_ids = info.attachment_ids
    	this._rpc({
    		fields: [
            	'memo', 'parent_directory', 
            	'size', 'id','attachment_ids'
				],
            domain: [
            	['id', '=', line_id]
            ],
            model: 'petty.cash.line',
            method: 'search_read',
            context: session.user_context,
        }).then(function(settings) {
        	_.each(settings, function(setting, index, settings) {
    			var data_part_file = $.Deferred();
    			data_parts.push(data_part_file);
        		self._rpc({
        			fields: [
	                	'name', 'mimetype', 'extension', 
	  				  	'cash_line_id', 'size',
	  				],
	                domain: [
	                	['id', 'in', attachment_ids],['cash_line_id', 'in', [line_id]]
	                ],
	                model: 'ir.attachment',
	                method: 'search_read',
	                context: session.user_context,
                }).then(function(files) {
                	settings[index].top_files = files;
                	data_part_file.resolve(files);
                });
        	});
        	$.when.apply($, data_parts).then(function() {
            	data_loaded.resolve(settings);
        	});
        });
        return data_loaded;
    },
	   
	   render: function() {
		   var self = this;
	        this.$tree = this.$el.find('.oe_document_tree').jstree({	
	        	'core' : {
	        		'animation': 0,
	        		'widget': self,
	        		'multiple': true,
	        		'check_callback': self._check_callback,
	        		'themes': {
	                    'name': 'proton',
	                    'responsive': true
	                },
	                'data': function (node, callback) {
	        			if(node.id === "#") {
	        				self._load_data().then(function(settings) {
	        					callback.call(this, _.map(settings, function (setting) {
	        						var child_directories = _.map(setting.top_directories, function (directory) {
	        							return self._node_directory(directory);
	        						});
	        						var child_files =_.map(setting.top_files, function (file) {
	        							return self._node_file(file);
	        						});
	        						return {
	        							id: "setting_" + setting.id,
	        							text: setting.memo,
	        							icon: "fa fa-folder-o",
	        	  	        			type: "settings",
	        	  	        			data: {
	        		        				odoo_id: setting.id,
	        		        				odoo_model: "petty.cash.line",
	        		        			},
	        		        			children: child_directories.concat(child_files),
	        		                  };
	        					}));
	        				});
	        	    	} else {
	        	    		self._load_node(node).then(function(node) {
	        	    			callback.call(this, node);
	        	    		});
	        	    	}
	        		},
	        	},
	        }).on('open_node.jstree', function (e, data) {
	    		if(data.node.data && data.node.data.odoo_model === "petty.cash.line") {
	    			data.instance.set_icon(data.node, "fa fa-folder-open-o"); 
	    		}
	    	}).on('close_node.jstree', function (e, data) { 
	    		if(data.node.data && data.node.data.odoo_model === "petty.cash.line") {
	        		data.instance.set_icon(data.node, "fa fa-folder-o"); 
	    		}
	    	}).on('changed.jstree', function (e, data) {
	    		self._update_jstree(data);
	    	});
	    },
	   
	    _load_node(node) {
	    	var self = this;
	    	var result = $.Deferred();
	    	var directories_query = $.Deferred();
	    	var info = JSON.parse(this.value);
			var line_id = info.line_id
			var title = info.title
			var attachment_ids = info.attachment_ids
	    		var directories_loaded = $.Deferred();
	    		var files_loaded = $.Deferred();
	    		this._rpc({
	                fields: [
	                	'memo', 'parent_directory', 
	                	'size', 'id','attachment_ids'
	  				],
	                domain: [
	                	['id', '=', line_id]
	                ],
	                model: 'petty.cash.line',
	                method: 'search_read',
	                context: session.user_context,
	            }).then(function(directories) {
	            	directories_loaded.resolve(_.map(directories, function (directory) {
	            		return self._node_directory(directory);
					}));
	            });
	    		
	    		this._rpc({
	                fields: [
	                	'name', 'mimetype', 'extension', 
	  				  	'cash_line_id', 'size',
	  				],
	                domain: [
	                	['id', 'in', attachment_ids],['cash_line_id', 'in', [line_id]]
	                ],
	                model: 'ir.attachment',
	                method: 'search_read',
	                context: session.user_context,
	            }).then(function(files) {
	            	files_loaded.resolve(_.map(files, function (file) {
						return self._node_file(file);
					}));
	            });
	    		$.when(directories_loaded, files_loaded).then(function(directories, files) {
	    			result.resolve(directories.concat(files));
	    		});
	    	return result;
	    },
	    _node_directory(directory) {
	    	return {
				id: "directory_" + directory.id,
				text: directory.memo,
				icon: "fa fa-folder-o",
				type: "directory",
				data: {
					odoo_id: directory.id,
					odoo_model: "petty.cash.line",
					name: directory.memo,
					size: dms_utils.format_size(directory.size),
				},
			}
	    },
	    _node_file(file) {
	    	return {
				id: "file_" + file.id,
				text: file.name,
				icon: dms_utils.mimetype2fa(file.mimetype, {prefix: "fa fa-"}),
				type: "file",
				data: {
					odoo_id: file.id,
					odoo_model: "ir.attachment",
					name: file.name,
					size: dms_utils.format_size(file.size),
					mimetype: file.mimetype,
					extension: file.extension,
				},
			}
	    },
	    
	    _check_callback: function (operation, node, parent, position, more) {
	    	if(operation === "copy_node" || operation === "move_node") {
	    		// prevent moving a root node
	    		if(node.parent === "#") {
	    			return false;
	            }
	    		// prevent moving a child above or below the root
	    		if(parent.id === "#") {
	    			return false;
		        }
	    		// prevent moving a child to a file
	    		if(parent.data && parent.data.odoo_model === "ir.attachment") {
	    			return false;
	            }
	    	}
	    	if(operation === "move_node") {
	    		// prevent duplicate names
	    		if(node.data && parent.data) {
	    			var self = this;
	    			var names = [];
	    			_.each(parent.children, function(child, index, children) {
	    				var child_node = self.get_node(child);
	    				if(child_node.data && child_node.data.odoo_model === parent.data.odoo_model) {
	    					names.push(child_node.data.name);
	    				}
	    			});
	    			if(names.indexOf(node.data.name) > -1) {
	    				return false;
	    			}
	            }
	        }
	    	return true;
	    },
	    
	    _preview_node: function(node) {
	    	var self = this;
	    	if(node.data && node.data.odoo_model === "ir.attachment") {
	    		PreviewHelper.createFilePreviewContent(node.data.odoo_id, self).then(function($content) {
	    			self.$el.find('.oe_document_preview').html($content);
	    		});
	    	} else if(node.data && node.data.odoo_model === "petty.cash.line") {
	    		return 
	    	}
	    },
	    
	    _update_jstree: function(data) {
	    	this._preview_node(data.node);
	    },
});

field_registry.add('attachmnet', ShowAttachmnetWidget);

});
