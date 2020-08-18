from odoo import models, fields, api, _ 
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, float_compare, pycompat

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	use_manual_rate = fields.Boolean(readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	auto_currency_rate = fields.Float(related='currency_id.rate', digits=(12, 6))
	manual_currency_rate = fields.Float(digits=(12, 6), readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')

	@api.one
	@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding','currency_id', 'company_id', 'date_invoice', 'type')
	def _compute_amount(self):
		round_curr = self.currency_id.round
		self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
		self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
		self.amount_total = self.amount_untaxed + self.amount_tax
		amount_total_company_signed = self.amount_total
		amount_untaxed_signed = self.amount_untaxed
		if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
			currency_id = self.currency_id.with_context(date=self.date_invoice)
			amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
			amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
			if self.use_manual_rate and self.type in ['in_invoice','in_refund']:
				# amount_total_company_signed = self.amount_total * self.manual_currency_rate
				# amount_untaxed_signed = self.amount_untaxed * self.manual_currency_rate
				amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id, True, self.manual_currency_rate)
				amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id, True, self.manual_currency_rate)
		sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		_logger.info("YOYOYOUO")
		_logger.info(amount_total_company_signed)
		_logger.info(amount_untaxed_signed)
		self.amount_total_company_signed = amount_total_company_signed * sign
		self.amount_total_signed = self.amount_total * sign
		self.amount_untaxed_signed = amount_untaxed_signed * sign

	# @api.one
	# @api.depends(
	# 	'state', 'currency_id', 'invoice_line_ids.price_subtotal',
	# 	'move_id.line_ids.amount_residual',
	# 	'move_id.line_ids.currency_id')
	# def _compute_residual(self):
	# 	residual = 0.0
	# 	residual_company_signed = 0.0
	# 	sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
	# 	for line in self.sudo().move_id.line_ids:
	# 		if line.account_id == self.account_id:
	# 			residual_company_signed += line.amount_residual
	# 			if line.currency_id == self.currency_id:
	# 				residual += line.amount_residual_currency if line.currency_id else line.amount_residual
	# 			else:
	# 				from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
	# 				if self.use_manual_rate and self.type in ['in_invoice','in_refund']:
	# 					residual += from_currency.compute(line.amount_residual, self.currency_id, True, self.manual_currency_rate)
	# 				else:
	# 					residual += from_currency.compute(line.amount_residual, self.currency_id)
	# 	self.residual_company_signed = abs(residual_company_signed) * sign
	# 	self.residual_signed = abs(residual) * sign
	# 	self.residual = abs(residual)
	# 	digits_rounding_precision = self.currency_id.rounding
	# 	if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
	# 		self.reconciled = True
	# 	else:
	# 		self.reconciled = False

	@api.multi
	def compute_invoice_totals(self, company_currency, invoice_move_lines):
		total = 0
		total_currency = 0
		for line in invoice_move_lines:
			if self.currency_id != company_currency:
				currency = self.currency_id.with_context(date=self.date or self.date_invoice or fields.Date.context_today(self))
				if not (line.get('currency_id') and line.get('amount_currency')):
					line['currency_id'] = currency.id
					line['amount_currency'] = currency.round(line['price'])
					# line['price'] = currency.compute(line['price'], company_currency)
					_logger.info("JKJL:JK")
					if self.use_manual_rate:
						line['price'] = currency.compute(line['price'], company_currency, True, self.manual_currency_rate)
						_logger.info(line['price'])
					else:
						line['price'] = currency.compute(line['price'], company_currency)
						_logger.info(line['price'])
			else:
				line['currency_id'] = False
				line['amount_currency'] = False
				line['price'] = self.currency_id.round(line['price'])
			if self.type in ('out_invoice', 'in_refund'):
				total += line['price']
				total_currency += line['amount_currency'] or line['price']
				line['price'] = - line['price']
			else:
				total -= line['price']
				total_currency -= line['amount_currency'] or line['price']
		return total, total_currency, invoice_move_lines

class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"

	@api.one
	@api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
		'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
		'invoice_id.date_invoice')
	def _compute_price(self):
		currency = self.invoice_id and self.invoice_id.currency_id or None
		price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
		taxes = False
		if self.invoice_line_tax_ids:
			taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
		self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
		self.price_total = taxes['total_included'] if taxes else self.price_subtotal
		if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
			if self.invoice_id.use_manual_rate and self.invoice_id.type in ['in_invoice','in_refund']:
				price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id, True, self.invoice_id.manual_currency_rate)
			else:
				price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
		sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
		self.price_subtotal_signed = price_subtotal_signed * sign