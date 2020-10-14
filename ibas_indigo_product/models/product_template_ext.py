# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IndigoProducts(models.Model):
    _inherit = 'product.template'

    retail_price = fields.Float(string='Retail Price')