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
