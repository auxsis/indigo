from odoo import models, fields, api, _

from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
        
    def action_compute_residual(self):
        for line in self.line_ids:
            line._amount_residual()
        return True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    invoice_state = fields.Selection([
        ('draft','Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Invoice Status', related='invoice_id.state', store=True)
    
#     @api.multi
#     def write(self, vals):
#         for line in self:
#             _logger.info(vals.get("statement_date"))
#             amount_residual_currency = vals.get("amount_residual_currency")
#             _logger.info(amount_residual_currency)
#             if not vals.get("statement_date") and amount_residual_currency == 0:
#                 _logger.info("HELLO")
#                 vals.update({"reconciled": True})
#         res = super(AccountMoveLine, self).write(vals)
#         return res