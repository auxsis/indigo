# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    ctns = fields.Integer()
    tgw = fields.Integer()
    tnw = fields.Integer()
    total_volume = fields.Integer()
    pcs_ctn = fields.Integer()
    length = fields.Integer()
    weight = fields.Integer()
    height = fields.Integer()
    gw = fields.Integer()
    nw = fields.Integer()
