from odoo import models, fields, api, _ 
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, float_compare, pycompat

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	picking_type = fields.Selection([
		('deliver','Delivery'),
		('pick','Pick'),
		('ship','Shipment'),
	], string='Batch Picking Type')
	picking_batch_id = fields.Many2one('stock.picking.batch', string='Add Batch Picking', readonly=True, states={'draft': [('readonly', False)]}, 
		help='Encoding help. When selected, the associated purchase order lines are added to the vendor bill. Several Batch Picking can be selected.')

	# Load all unsold PO lines
	@api.onchange('picking_batch_id')
	def picking_batch_change(self):
		if not self.picking_batch_id:
			return {}
		# if not self.partner_id and self.picking_batch_id.partner_id:
		# 	self.partner_id = self.picking_batch_id.partner_id.id

		new_lines = self.env['account.invoice.line']
		for picking in self.picking_batch_id.picking_ids:
			
			for line in picking.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
				data = self._prepare_invoice_line_from_po_line(line)
				new_line = new_lines.new(data)
				new_line._set_additional_fields(self)
				new_lines += new_line

		self.invoice_line_ids += new_lines
		# self.payment_term_id = self.purchase_id.payment_term_id
		self.env.context = dict(self.env.context, from_purchase_order_change=True)
		self.picking_batch_id = False
		return {}