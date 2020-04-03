from odoo import models, fields, api, _ 

class AccountBankStatementLine(models.Model):
	_inherit = 'account.bank.statement.line'

	bank_location = fields.Char()
	# check_number = fields.Char()