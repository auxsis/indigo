from odoo import models, fields, api, _ 

class AccountCheque(models.Model):
	_inherit = "account.cheque"

	# NEW
	bank_id = fields.Many2one('res.bank', string='Bank')
	bank_account_number_id = fields.Many2one('res.partner.bank', string='Bank Account Number')

	# OVERRIDE
	name = fields.Char(string="Name", required=False, related='sequence')

	@api.onchange('sequence')
	def set_name(self):
		self.name = self.sequence