# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

from odoo.tools.misc import formatLang


class IbasBatchPick(models.Model):
    _inherit = 'stock.picking.batch'

    bill_status = fields.Selection([
        ('open', 'open'),
        ('paid', 'paid')
    ], string='Bill Status')

    
    