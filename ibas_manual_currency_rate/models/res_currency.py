from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
	_inherit = 'res.currency'

	# use_manual_rate = fields.Boolean()
	# manual_currency_rate = fields.Float(digits=(12, 6))

	# @api.model
	# def _get_conversion_rate(self, from_currency, to_currency):
	# 	from_currency = from_currency.with_env(self.env)
	# 	to_currency = to_currency.with_env(self.env)
	# 	currency_rate = to_currency.rate / from_currency.rate
	# 	if from_currency.use_manual_rate:
	# 		currency_rate = from_currency.manual_currency_rate
	# 	elif to_currency.use_manual_rate:
	# 		currency_rate = to_currency.manual_currency_rate
	# 	return currency_rate

	@api.model
	def _compute(self, from_currency, to_currency, from_amount, round=True, manual_rate=False):
		if (to_currency == from_currency):
			amount = to_currency.round(from_amount) if round else from_amount
		else:
			rate = self._get_conversion_rate(from_currency, to_currency)
			# GET MANUAL RATE
			if manual_rate:
				rate = manual_rate
			amount = to_currency.round(from_amount * rate) if round else from_amount * rate
		return amount

	@api.multi
	def compute(self, from_amount, to_currency, round=True, manual_rate=False):
		""" Convert `from_amount` from currency `self` to `to_currency`. """
		self, to_currency = self or to_currency, to_currency or self
		assert self, "compute from unknown currency"
		assert to_currency, "compute to unknown currency"
		# apply conversion rate
		if self == to_currency:
			to_amount = from_amount
		else:
			to_amount = from_amount * self._get_conversion_rate(self, to_currency)
			# GET TOTAL FROM MANUAL RATE
			if manual_rate:
				to_amount = from_amount * manual_rate
		# apply rounding
		return to_currency.round(to_amount) if round else to_amount