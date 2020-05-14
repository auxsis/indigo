from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cheque_note = fields.Text(string='Cheque Notes')

    # The name is attributed upon post()
    name = fields.Char(readonly=False, copy=False)
