from odoo import models, fields, api, _ 
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt

import logging
_logger = logging.getLogger(__name__)

class ReportStockAging(models.AbstractModel):
	_name = 'report.ibas_stock_aging_report.report_stock_aging'

	@api.model
	def get_report_values(self, docids, data=None):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		return {
			'data': data['form'],
			'lines': self.get_lines(data.get('form')),
		}

	def _compute_from_smls(self, date_from, date_to, location, product):
		_logger.info(location)
		_logger.info(date_from)
		_logger.info(date_to)
		if product:		
			self.env.cr.execute("SELECT move.product_id AS product_id, SUM(move.product_uom_qty) AS product_uom_qty "
				"FROM stock_move move "
				"WHERE move.date >= %s and move.date <= %s and move.location_dest_id = %s and move.product_id = %s "
				"GROUP BY move.product_id", (date_from, date_to, location, product))
		else:
			self.env.cr.execute("SELECT move.product_id AS product_id, SUM(move.product_uom_qty) AS product_uom_qty "
				"FROM stock_move move "
				"WHERE move.date >= %s AND move.date <= %s AND move.location_dest_id = %s "
				"GROUP BY move.product_id", (date_from, date_to, location))
		results = self.env.cr.dictfetchall()
		_logger.info(results)
		return results

	@api.model
	def get_lines(self, options):
		groups = []

		_logger.info("HELLO")

		location = int(options['location_id'][0])
		# category = int(options['category_id'][0])

		product = False
		if options['product_id']:
			product = int(options['product_id'][0])
		period = int(options['period'])
		period_group = 5

		
		_logger.info(period)

		date_from_group = False
		# date_to_group = False

		for group in range(1, period_group):
			_logger.info(group)
			if date_from_group:
				date_from = date_from_group
			else:
				date_from = datetime.strptime(options['date'], '%Y-%m-%d')
			date_to = date_from + timedelta(days=period)
			date_from_group = date_to 
			period_group_result = self._compute_from_smls(date_from, date_to, location, product)

			for result in period_group_result:
				period_result = dict(result)

				product_id = result.get('product_id')
				product_uom_qty = result.get('product_uom_qty')
				product_name = ''
				product_data = self.env['product.product'].browse(product_id)
				if product_data:
					product_name = product_data.display_name

				period_result['product_name'] = product_name
				if group == 1:
					period_result['period_1'] = product_uom_qty
				elif group == 2:
					period_result['period_2'] = product_uom_qty
				elif group == 3:
					period_result['period_3'] = product_uom_qty
				elif group == 4:
					period_result['period_4'] = product_uom_qty
				elif group == 5:
					period_result['period_5'] = product_uom_qty

				groups.append(period_result)

		_logger.info(groups)
		return groups