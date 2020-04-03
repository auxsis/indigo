from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	# OVERRIDE TO SET INVOICE DATE BASED ON SALES CONFIRMATION DATE / TO BE REMOVED AFTER DATA ENCODING
	@api.model
	def create(self, vals):
		if vals.get('origin'):
			sale_order = self.env['sale.order'].search([('name','=',vals.get('origin'))], limit=1)
			if sale_order:
				vals['date_invoice'] = sale_order.confirmation_date

		result = super(AccountInvoice, self).create(vals)

		return result