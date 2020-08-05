# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import logging

from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)


class ibASAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    shipment_ids = fields.Many2many('stock.picking.batch', string='Shipments')

    def resolve_shipments(self):
        for rec in self:
            orderlines = []
            for shipment in self.shipment_ids:
                for pick_item in shipment.move_ids:
                    orderlines.append((0,0,{
                        'product_id': pick_item.product_id.id,
                        'purchase_line_id': pick_item.purchase_line_id.id,
                        'name': pick_item.product_id.name,
                        'account_id': pick_item.product_id.categ_id.property_stock_account_input_categ_id.id,
                        'quantity': pick_item.product_uom_qty,
                        'price_unit': pick_item.purchase_line_id.price_unit,
                        'orig_price_unit': pick_item.purchase_line_id.price_unit

                    }))

            self.invoice_line_ids = orderlines
    
    def action_invoice_open(self):
       
        for rec in self:
            if rec.type == "in_invoice":    
                for line in rec.invoice_line_ids:
                    try:
                        line.product_id.standard_price = line.price_unit
                        line.purchase_line_id.move_ids[0].value = line.price_unit * line.quantity
                        line.purchase_line_id.move_ids[0].remaining_value = line.price_unit * line.quantity
                        
                        _logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                    except:
                        _logger.debug("XXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                        pass
                    
                for shipment in rec.shipment_ids:
                    shipment.bill_status = 'paid'
        
        super(ibASAccountInvoice, self).action_invoice_open()
    