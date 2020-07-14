# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from datetime import datetime

class StockPickingBatch(models.Model):

    _inherit = 'stock.picking.batch'

    def _get_account(self, product):
        if product.property_account_expense_id:
            return product.property_account_expense_id.id
        elif product.categ_id and product.categ_id.property_account_expense_categ_id:
            return product.categ_id.property_account_expense_categ_id.id
        else:
            raise Warning(_("One of product does not has configured expense account!"))


    def _get_invoice_account(self, partner_id):

        partner = self.env['res.partner'].browse(partner_id)

        if partner.property_account_payable_id:
            return partner.property_account_payable_id.id
        else:
            raise Warning(_("Accounts are not configures inside vendor!"))


    def _product_unit_price(self, product_id, picking):

        if picking and picking.purchase_id:
            for purchase_line in picking.purchase_id.order_line:
                if purchase_line.product_id.id == product_id.id:
                    return purchase_line.price_unit
        else:
            return product_id.standard_price

    def create_bill(self):
        origin_list = []
        partner_id = self.env['ir.config_parameter'].sudo().get_param('jt_picking_batch_bill.default_vendor_id')
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        for rec in self.picking_ids:
            if rec.origin:
                origin_list.append(rec.origin)
            else:
                False
            vals = {
                'partner_id': int(partner_id),
                'account_id': self._get_invoice_account(partner_id),
                'type': 'in_invoice',
                'date_invoice': datetime.today(),
                'origin': ', '.join(origin_list) or False,
                'reference': self.name,
            }
        invoice_id = invoice_obj.create(vals)
        for picking in self.picking_ids:
            for line in picking.move_lines:
                line_vals = {
                    'invoice_id': invoice_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity_done,
                    'name': line.product_id.name,
                    'account_id': self._get_account(line.product_id),
                    'price_unit': self._product_unit_price(line.product_id, picking),
                    'purchase_id': picking.origin or False,
                }
                invoice_line_obj.create(line_vals)
        return {
            'name':self.name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.invoice',
            'res_id': invoice_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('type','=','in_invoice')]",
        }


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'


    @api.multi
    def write(self, vals):
        """ When editing a done stock.move.line, we impact the valuation. Users may increase or
        decrease the `qty_done` field. There are three cost method available: standard, average
        and fifo. We implement the logic in a similar way for standard and average: increase
        or decrease the original value with the standard or average price of today. In fifo, we
        have a different logic wheter the move is incoming or outgoing. If the move is incoming, we
        update the value and remaining_value/qty with the unit price of the move. If the move is
        outgoing and the user increases qty_done, we call _run_fifo and it'll consume layer(s) in
        the stack the same way a new outgoing move would have done. If the move is outoing and the
        user decreases qty_done, we either increase the last receipt candidate if one is found or
        we decrease the value with the last fifo price.
        """

        if 'qty_done' in vals:
            moves_to_update = {}
            for move_line in self.filtered(lambda ml: ml.state == 'done' and (ml.move_id._is_in() or ml.move_id._is_out())):
                moves_to_update[move_line.move_id] = vals['qty_done'] - move_line.qty_done

            for move_id, qty_difference in moves_to_update.items():
                move_vals = {}
                if move_id.product_id.cost_method in ['standard', 'average']:
                    if move_id.product_id.purchase_line_id:
                        correction_value = qty_difference * move_id.product_id.purchase_line_id.unit_price
                    else:
                        correction_value = qty_difference * move_id.product_id.standard_price
                    if move_id._is_in():
                        move_vals['value'] = move_id.value + correction_value
                    elif move_id._is_out():
                        move_vals['value'] = move_id.value - correction_value
                else:
                    if move_id._is_in():
                        correction_value = qty_difference * move_id.price_unit
                        new_remaining_value = move_id.remaining_value + correction_value
                        move_vals['value'] = move_id.value + correction_value
                        move_vals['remaining_qty'] = move_id.remaining_qty + qty_difference
                        move_vals['remaining_value'] = move_id.remaining_value + correction_value
                    elif move_id._is_out() and qty_difference > 0:
                        correction_value = self.env['stock.move']._run_fifo(move_id, quantity=qty_difference)
                        # no need to adapt `remaining_qty` and `remaining_value` as `_run_fifo` took care of it
                        move_vals['value'] = move_id.value - correction_value
                    elif move_id._is_out() and qty_difference < 0:
                        candidates_receipt = self.env['stock.move'].search(move_id._get_in_domain(), order='date, id desc', limit=1)
                        if candidates_receipt:
                            candidates_receipt.write({
                                'remaining_qty': candidates_receipt.remaining_qty + -qty_difference,
                                'remaining_value': candidates_receipt.remaining_value + (-qty_difference * candidates_receipt.price_unit),
                            })
                            correction_value = qty_difference * candidates_receipt.price_unit
                        else:
                            correction_value = qty_difference * move_id.product_id.standard_price
                        move_vals['value'] = move_id.value - correction_value
                move_id.write(move_vals)

                if move_id.product_id.valuation == 'real_time':
                    move_id.with_context(force_valuation_amount=correction_value, forced_quantity=qty_difference)._account_entry_move()
                if qty_difference > 0:
                    move_id.product_price_update_before_done(forced_qty=qty_difference)
        return super(StockMoveLine, self).write(vals)