/** -*- coding: utf-8 -*-
 Odoo, Open Source Itm Petty Cash.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */
$.fn.textWidth = function(text, font) {
    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);
    $.fn.textWidth.fakeEl.text(text || this.val() || this.text()).css('font', font || this.css('font'));
    return $.fn.textWidth.fakeEl.width();
};

$.fn.dndHover = function(options) {
    return this.each(function() {
        var self = $(this);
        var collection = $();
        self.on('dragenter', function(event) {
            if (collection.size() === 0) {
                self.trigger('dndHoverStart');
            }
            collection = collection.add(event.target);
        });
        self.on('dragleave', function(event) {
            setTimeout(function() {
                collection = collection.not(event.target);
                if (collection.size() === 0) {
                    self.trigger('dndHoverEnd');
                }
            }, 1);
        });
        self.on('drop', function(event) {
            setTimeout(function() {
            	collection = $();
            	self.trigger('dndHoverEnd');
            }, 1);
        });
    });
};