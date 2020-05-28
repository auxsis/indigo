from odoo import models, fields, api, _ 
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)

class StockPickingBatch(models.Model):
	_inherit = 'stock.picking.batch'

	date = fields.Date(default=fields.Datetime.now())
	reference = fields.Char(string='Reference Number')
	picking_type = fields.Selection([
		('deliver','Delivery'),
		('pick','Pick'),
		('ship','Shipment'),
	], string='Type')
	move_ids = fields.Many2many('stock.move', compute='_get_picking_move')

	@api.multi
	def _get_picking_move(self):
		for record in self:
			move_lines = []
			for picking in record.picking_ids:
				for move in picking.move_lines:
					move_lines.append(move.id)
			record.move_ids = move_lines

	@api.multi
	def name_get(self):
		result = []
		for batch in self:
			name = batch.name
			if batch.reference:
				name += ' ('+batch.reference+')'
			result.append((batch.id, name))
		return result
	
	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=100):
		if operator in ('ilike', 'like', '=', '=like', '=ilike'):
			domain = expression.AND([
				args or [],
				['|', ('name', operator, name), ('reference', operator, name)]
			])
			return self.search(domain, limit=limit).name_get()
		return super(StockPickingBatch, self).name_search(name, args, operator, limit)