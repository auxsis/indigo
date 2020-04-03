from odoo import models, fields, api, _ 

class StockAgingReport(models.TransientModel):
	_name = 'stock.aging.report'
	_description = 'Stock Aging Report'

	def _default_warehouse(self):
		warehouse_id = self.env['stock.warehouse'].search([('company_id','=',self.env.user.company_id.id)], limit=1)
		return warehouse_id.id or False

	def _default_location(self):
		warehouse_id = self.env['stock.warehouse'].search([('company_id','=',self.env.user.company_id.id)], limit=1)
		return warehouse_id.lot_stock_id.id or False

	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, default=lambda self: self._default_warehouse())
	location_id = fields.Many2one('stock.location', string='Location', required=True, default=lambda self: self._default_location())
	category_id = fields.Many2one('product.category', string='Product Category')
	product_id = fields.Many2one('product.product', string='Product')
	period = fields.Integer(string='Period Length (days)', required=True)
	date = fields.Date(string='Date', required=True, default=fields.Datetime.now())

	def _build_contexts(self, data):
		result = {}
		result['company_id'] = data['form']['company_id'] or False
		result['warehouse_id'] = data['form']['warehouse_id'] or False
		result['location_id'] = data['form']['location_id'] or False
		result['category_id'] = data['form']['category_id'] or False
		result['product_id'] = 'product_id' in data['form'] and data['form']['product_id'] or False
		result['period'] = data['form']['period'] or 0
		result['date'] = data['form']['date'] or False
		return result

	def _print_report(self, data):
		return self.env.ref('ibas_stock_aging_report.action_report_stock_aging').report_action(self, data=data)         

	@api.multi
	def print_report(self):
		self.ensure_one()
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['company_id', 'warehouse_id', 'location_id', 'category_id', 'product_id', 'period', 'date'])[0]
		used_context = self._build_contexts(data)
		data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
		return self._print_report(data)