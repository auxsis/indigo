from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import datetime

import logging

_logger = logging.getLogger(__name__)

class StockPickItemReport(models.TransientModel):
	_name = 'stock.pick.item.report'
	_description = 'Stock Pick Item'

	date_from = fields.Date(string='Date From', default=fields.Datetime.now)
	date_to = fields.Date(string='Date To', default=fields.Datetime.now)
	user_id = fields.Many2one('res.users', string='Salesperson')


	def _print_report(self, data):
		context = self._context
		filename = 'stock_pick_item_report.xls'
		date_from = data['date_from']['date_from']
		date_to = data['date_to']['date_to']
		user_id = data['user_id']['user_id']
		if user_id:
			user_id = data['user_id']['user_id'][0]

		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/export_xls/stock_pick_item_report?filename=%s&date_from=%s&date_to=%s&user_id=%s'%(filename,date_from,date_to,user_id),
			'target': 'self',
		}

	@api.multi
	def check_report(self):
		self.ensure_one()
		data = {}
		data['date_from'] = self.read(['date_from'])[0]
		data['date_to'] = self.read(['date_to'])[0]
		data['user_id'] = self.read(['user_id'])[0]
		return self._print_report(data)