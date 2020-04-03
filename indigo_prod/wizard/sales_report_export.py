from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import xlwt
from xlsxwriter.workbook import Workbook
import datetime

import logging

_logger = logging.getLogger(__name__)

class SalesReportExport(models.TransientModel):
	_name = 'sales.report.export'
	_description = 'Export Sales Report'

	# @api.multi
	# def _get_orders(self):
	# 	context = self._context
	# 	ids = context['active_ids']
	# 	_logger.info('JEJEKA')
	# 	_logger.info(context['active_ids'])

	# 	self.update({
	# 		'sale_ids': [[6, False, ids]]
	# 	})

	# sale_ids = fields.Many2many('sale.order', compute='_get_orders')

	def _print_report(self, data):
		context = self._context
		filename = 'sales_report.xls'
		sale_ids = context['active_ids']
		date_from = False
		date_to = False
		
		# CHECK IF ADMIN
		is_admin = False
		user = self.env['res.users'].browse(self.env.uid)
		if user.has_group('base.group_erp_manager'):
			is_admin = True
		
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/export_xls/sales_report?filename=%s&sale_ids=%s&date_from=%s&date_to=%s,&is_admin=%s'%(filename,sale_ids,date_from,date_to,is_admin),
			'target': 'self',
		}

	@api.multi
	def check_report(self):
		self.ensure_one()
		data = {}
		return self._print_report(data)

class SalesReport(models.TransientModel):
	_name = 'sales.report'
	_description = 'Sales Report'

	date_from = fields.Date(string='Date From', default=fields.Datetime.now)
	date_to = fields.Date(string='Date To', default=fields.Datetime.now)

	def _print_report(self, data):
		context = self._context
		filename = 'sales_report.xls'
		sale_ids = False
		date_from = data['date_from']['date_from']
		date_to = data['date_to']['date_to']
		
		# CHECK IF ADMIN
		is_admin = False
		user = self.env['res.users'].browse(self.env.uid)
		if user.has_group('base.group_erp_manager'):
			is_admin = True

		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/export_xls/sales_report?filename=%s&sale_ids=%s&date_from=%s&date_to=%s&is_admin=%s'%(filename,sale_ids,date_from,date_to,is_admin),
			'target': 'self',
		}

	@api.multi
	def check_report(self):
		self.ensure_one()
		data = {}
		data['date_from'] = self.read(['date_from'])[0]
		data['date_to'] = self.read(['date_to'])[0]
		return self._print_report(data)