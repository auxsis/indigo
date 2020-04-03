# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IBASSaleIndigo(models.Model):
    _inherit = 'sale.order.line'
    margin_percent = fields.Float(compute='_compute_margin_percent', string='Margin %', store=True,digits=(12,2))
    
    @api.depends('price_unit','purchase_price')
    def _compute_margin_percent(self):
        for rec in self:
            if rec.purchase_price > 0:
                rec.margin_percent = ((rec.price_unit - rec.purchase_price) / rec.purchase_price) * 100
            else:
                rec.margin_percent = 100

class IBASSaleOrder(models.Model):
    _inherit = 'sale.order'

    total_margin_percent = fields.Float(compute='_compute_total_margin_percent', string='Total Margin %', 
    store=True,digits=(12,2))
    
    @api.depends('amount_total')
    def _compute_total_margin_percent(self):
        for rec in self:
            total_cost = 0
            for sale_line in rec.order_line:
                total_cost = total_cost + sale_line.margin_percent
            
            if total_cost > 0:
                rec.total_margin_percent = total_cost / len(rec.order_line)


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