

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Partners(models.Model):
    _inherit = 'res.partner'

    partner_area_id = fields.Many2one(
        'indigo_prod.partner_area',
        string='Partner Area',
    )

    primary_contact_person = fields.Char(
        string='Contact Person',
    )



class PartnerArea(models.Model):
    _name = 'indigo_prod.partner_area'

    name = fields.Char(
        string='Partner Area',
        required=True
    )


class IndigoSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_quantity = fields.Float(
        string='Available Quantity',
        compute="_value_available_quantity"
    )

    product_model = fields.Char(
        string='Model',
        compute="_value_available_quantity"
    )

    @api.multi
    @api.onchange('product_id', 'product_uom_qty')
    def _value_available_quantity(self):
        for rec in self:
            rec.product_model = rec.product_id.carmodel_id.name
            rec.available_quantity = rec.product_id.virtual_available

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id_indigo(self):
        if (self.product_id and self.order_id.partner_id):
            previous_orders = self.env['sale.order.line'].search([("order_id.partner_id", "=", self.order_id.partner_id.id),
                                                                  ("product_id", "=", self.product_id.id)], order="id desc", limit=5)

            message = ""
            for rec in previous_orders:
                message = (message + "Sales Order #:" + rec.order_id.name + " Order Date:" + str(rec.order_id.date_order)
                           + '\n' + " Quantity:" + str(rec.product_uom_qty)
                           + " Unit Price:" + str(rec.price_unit) + " Discount:" + str(
                               rec.discount) + " Subtotal:" + str(rec.price_subtotal) + '\n'
                           + '\n')
                _logger.info(rec.order_id.name)

            if (message):
                warning = {}
                title = "Previous quotations for this customer and product"
                warning = {
                    'title': title,
                    'message': message,
                }
                return {'warning': warning}
