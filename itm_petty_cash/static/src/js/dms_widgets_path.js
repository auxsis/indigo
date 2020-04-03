/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
odoo.define('itm_petty_cash.path', function(require) {
"use strict";

var core = require('web.core');
var registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var field_widgets = require('web.basic_fields');

var _t = core._t;
var QWeb = core.qweb;

$.fn.textWidth = function(text, font) {
    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);
    $.fn.textWidth.fakeEl.text(text || this.val() || this.text()).css('font', font || this.css('font'));
    return $.fn.textWidth.fakeEl.width();
};

var FieldDocumentPath = field_widgets.FieldChar.extend({
	_renderReadonly: function() {
    	var show_value = this._formatValue(this.value);
    	var max_width = this.nodeOptions.width || 500;
    	var text_witdh = $.fn.textWidth(show_value);
    	if(text_witdh >= max_width) {
    		var ratio_start = (1 - (max_width / text_witdh)) * show_value.length;
    		show_value = ".." +  show_value.substring(ratio_start, show_value.length);
    	}
        this.$el.text(show_value);
	},
});


var FieldDocumentRelationalPath = field_widgets.InputField.extend({
	className: 'muk_form_relpath',
    supportedFieldTypes: ['text'],
    tagName: 'span',
    events : {
		'click a' : '_node_clicked',
	},
    init: function () {
        this._super.apply(this, arguments);
        if (this.mode === 'edit') {
            this.className = 'o_form_textarea';
            this.tagName = 'textarea';
        }
    },
    start: function () {
        if (this.mode === 'edit') {
            dom.autoresize(this.$el, {parent: this});
        }
        return this._super();
    },
    _renderReadonly: function() {
    	var self = this;
    	var text = "";
    	var path = JSON.parse(this.value || "[]");
    	var max_width = this.nodeOptions.width || 500;
    	this.$el.empty();
    	$.each(_.clone(path).reverse(), function(index, element) {
    		text += element.name + "/";
    		if($.fn.textWidth(text) >= max_width) {
        		self.$el.prepend($('<span/>').text(".."));
    		} else {
        		if (index == 0) {
        			if(element.model == 'petty.cash.line') {
            			self.$el.prepend($('<span/>').text(self.nodeOptions.seperator || "/"));
        			}
            		self.$el.prepend($('<span/>').text(element.name));
            		self.$el.prepend($('<span/>').text(self.nodeOptions.seperator || "/"));
        		} else {
        			var node = $('<a/>');
            		node.addClass("oe_form_uri");
            		node.data('model', element.model);
            		node.data('id', element.id);
            		node.attr('href', "javascript:void(0);");
            		node.text(element.name);
            		self.$el.prepend(node);
            		self.$el.prepend($('<span/>').text(self.nodeOptions.seperator || "/"));
        		}
    		}
    		return ($.fn.textWidth(text) < max_width);
    	});
    },
    _node_clicked : function(event) {
    	this.do_action({
			type: 'ir.actions.act_window',
			res_model: $(event.currentTarget).data('model'),
			res_id: $(event.currentTarget).data('id'),
			views: [[ false, 'form' ]],
			target: 'current',
			context: {},
		});
	}
});

registry.add('dms_path', FieldDocumentPath);
registry.add('dms_relpath', FieldDocumentRelationalPath);

return {
	FieldDocumentPath: FieldDocumentPath,
	FieldDocumentRelationalPath: FieldDocumentRelationalPath,
};

});
