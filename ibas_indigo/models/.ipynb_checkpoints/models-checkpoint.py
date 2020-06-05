# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class IBASSaleIndigo(models.Model):
    _inherit = 'sale.order.line'
    margin_percent = fields.Float(compute='_compute_margin_percent', string='Margin %', store=True, digits=(12,2))
    
    # Margin % = (Selling Price - Cost) / Selling Price
    # w/ Discount: Margin % = (Selling Price*(100% - Discount%) - Cost) / Selling Price*(100% - Discount%)
    @api.depends('price_unit','purchase_price','discount')
    def _compute_margin_percent(self):
        for rec in self:
            discount = (100 - rec.discount) / 100
            if rec.purchase_price > 0:
                #if rec.discount > 0:
                    #discount = (100 - rec.discount) / 100
                rec.margin_percent = ((rec.price_unit * discount - rec.purchase_price) / (rec.price_unit * discount)) * 100
                #else:
                    #rec.margin_percent = ((rec.price_unit - rec.purchase_price) / rec.purchase_price) * 100
            elif rec.purchase_price == 0 and rec.product_id.standard_price >  0 :
                #if rec.discount > 0:
                    #discount = (100 - rec.discount) / 100
                rec.margin_percent = ((rec.price_unit * discount - rec.product_id.standard_price) / (rec.price_unit * discount)) * 100
                #else:
                    #rec.margin_percent = ((rec.price_unit - rec.product_id.standard_price) / rec.product_id.standard_price) * 100
            else:
                rec.margin_percent = 100

class IBASSaleOrder(models.Model):
    _inherit = 'sale.order'

    total_margin_percent = fields.Float(compute='_compute_total_margin_percent', string='Total Margin %', 
    store=True,digits=(12,2))
    
    # Total Margin % = (Total - Total Cost) / Total
    @api.depends('amount_total')
    def _compute_total_margin_percent(self):
        for rec in self:
            total_cost = 0
            for line in rec.order_line:
                purchase_price = line.purchase_price * line.product_uom_qty
                total_cost += purchase_price
            
            if total_cost > 0:
                # rec.total_margin_percent = total_cost / len(rec.order_line)
                rec.total_margin_percent = ((rec.amount_total - total_cost) / rec.amount_total) * 100


# class ibas_indigo(models.Model):
#     _name = 'ibas_indigo.ibas_indigo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100