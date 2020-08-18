# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class IBASSaleIndigo(models.Model):
    _inherit = 'sale.order.line'
    margin_percent = fields.Float(
        compute='_compute_margin_percent', string='Margin %', store=True, digits=(12, 2))

    cost_per_line_item = fields.Float(
        string='Cost per Line Item', compute='_compute_cost_per_line')
    gross_profit = fields.Float(
        string='Gross Profit', compute='_compute_gross_profit')

    @api.depends('purchase_price', 'product_uom_qty')
    def _compute_cost_per_line(self):
        for rec in self:
            rec.cost_per_line_item = rec.product_uom_qty * rec.purchase_price

    @api.depends('cost_per_line_item', 'price_subtotal')
    def _compute_gross_profit(self):
        for rec in self:
            rec.gross_profit = rec.price_subtotal - rec.cost_per_line_item

    # Margin % = (Selling Price - Cost) / Selling Price
    # w/ Discount: Margin % = (Selling Price*(100% - Discount%) - Cost) / Selling Price*(100% - Discount%)
    @api.depends('price_unit', 'purchase_price', 'discount')
    def _compute_margin_percent(self):
        for rec in self:
            discount = (100 - rec.discount) / 100
            if rec.purchase_price > 0:
                # if rec.discount > 0:
                #discount = (100 - rec.discount) / 100
                rec.margin_percent = (
                    (rec.price_unit * discount - rec.purchase_price) / (rec.price_unit * discount)) * 100
                # else:
                #rec.margin_percent = ((rec.price_unit - rec.purchase_price) / rec.purchase_price) * 100
            elif rec.purchase_price == 0 and rec.product_id.standard_price > 0:
                # if rec.discount > 0:
                #discount = (100 - rec.discount) / 100
                rec.margin_percent = (
                    (rec.price_unit * discount - rec.product_id.standard_price) / (rec.price_unit * discount)) * 100
                # else:
                #rec.margin_percent = ((rec.price_unit - rec.product_id.standard_price) / rec.product_id.standard_price) * 100
            else:
                rec.margin_percent = 100


class IBASSaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('amount_total')
    def _compute_purchase_price(self):
        for record in self:
            total_purchase_price = 0
            for line in record.order_line:
                purchase_price = line.purchase_price * line.product_uom_qty
                total_purchase_price += purchase_price
            record.total_purchase_price = total_purchase_price

    total_purchase_price = fields.Float(
        compute='_compute_purchase_price', store=True, string='Total Cost')

    total_margin_percent = fields.Float(compute='_compute_total_margin_percent', string='Total Margin %',
                                        store=True, digits=(12, 2))

    gross_profit_total = fields.Monetary(
        string='Total Gross Profit', store=True, readonly=True, compute='_compute_gross_profit', tracking=6)

    @api.depends('order_line.gross_profit')
    def _compute_gross_profit(self):
        """
        Compute the total gross profit of the SO.
        """
        for order in self:
            gross = 0.0
            for line in order.order_line:
                gross += line.gross_profit
            order.update({
                'gross_profit_total': gross
            })

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
                rec.total_margin_percent = (
                    (rec.amount_total - total_cost) / rec.amount_total) * 100

    is_invoice = fields.Boolean(string='Is this an invoice?')
    vat = fields.Float(compute='_compute_VAT', string='VAT',
                       store=True, digits=(12, 2))

    @api.depends('amount_total', 'is_invoice')
    def _compute_VAT(self):
        for rec in self:
            if rec.is_invoice:
                rec.vat = (rec.amount_total - (rec.amount_total / 1.12))
            else:
                rec.vat = 0


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
