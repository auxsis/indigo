from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    invoice_state = fields.Selection([
        ('draft','Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Invoice Status', related='invoice_id.state', store=True)