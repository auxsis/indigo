from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class ReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'
	_description = 'Return Picking'

	return_type = fields.Many2one('stock.picking.return.type', 'Return Type')

	def _create_returns(self):
		# TODO sle: the unreserve of the next moves could be less brutal
		for return_move in self.product_return_moves.mapped('move_id'):
			return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

		# create new picking for returned products
		picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
		new_picking = self.picking_id.copy({
			'move_lines': [],
			'picking_type_id': picking_type_id,
			'state': 'draft',
			'origin': _("Return of %s") % self.picking_id.name,
			'location_id': self.picking_id.location_dest_id.id,
			'location_dest_id': self.location_id.id,
			'is_return':True,
			'return_type': self.return_type.id})
		new_picking.message_post_with_view('mail.message_origin_link',
			values={'self': new_picking, 'origin': self.picking_id},
			subtype_id=self.env.ref('mail.mt_note').id)
		returned_lines = 0
		for return_line in self.product_return_moves:
			if not return_line.move_id:
				raise UserError(_("You have manually created product lines, please delete them to proceed"))
			# TODO sle: float_is_zero?
			if return_line.quantity:
				returned_lines += 1
				vals = self._prepare_move_default_values(return_line, new_picking)
				r = return_line.move_id.copy(vals)
				vals = {}

				# +--------------------------------------------------------------------------------------------------------+
				# |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
				# |              | returned_move_ids              ↑                                  | returned_move_ids
				# |              ↓                                | return_line.move_id              ↓
				# |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
				# +--------------------------------------------------------------------------------------------------------+
				move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
				move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
				vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
				vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
				r.write(vals)
		if not returned_lines:
			raise UserError(_("Please specify at least one non-zero quantity."))

		new_picking.action_confirm()
		new_picking.action_assign()
		return new_picking.id, picking_type_id
