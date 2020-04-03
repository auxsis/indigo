# -*- coding: utf-8 -*-

from odoo import api, models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    analytc_account = fields.Many2one('account.analytic.account',string="Analytic Accounts")
