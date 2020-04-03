from odoo import models, fields, api, _ 

class AccountPayment(models.Model):
	_inherit = 'account.payment'

	cheque_note = fields.Text(string='Cheque Notes')