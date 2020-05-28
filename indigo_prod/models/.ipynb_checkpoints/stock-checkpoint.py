from odoo import models, fields, api, _ 

class StockPicking(models.Model):
	_inherit = "stock.picking"

	is_return = fields.Boolean()
	return_type = fields.Many2one('stock.picking.return.type', 'Return Type')
	purchase_partner_ref = fields.Char(related='purchase_id.partner_ref', string='Vendor Reference')

class ReturnPickingType(models.Model):
	_name = "stock.picking.return.type"
	_description = "Return Picking Type"

	name = fields.Char(string='Return Type')

class StockMove(models.Model):
	_inherit = "stock.move"

	purchase_partner_ref = fields.Char(related='picking_id.purchase_partner_ref', string='Vendor Reference')