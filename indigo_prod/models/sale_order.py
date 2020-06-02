# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)

class IndySaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _get_default_delivery(self):
        carrier_id = self.env['delivery.carrier'].search(
            [('default', '=', True)], limit=1)
        return carrier_id
    
    @api.multi
    def _compute_purchase_price(self):
        for record in self:
            total_purchase_price = 0
            for line in record.order_line:
                total_purchase_price += line.purchase_price
            record.total_purchase_price = total_purchase_price
                

    partner_id = fields.Many2one('res.partner', string='Customer', readonly=False, states={
    }, required=True, change_default=True, index=True, track_visibility='always')
    legacy_number = field_name = fields.Char()
    invoice_type = fields.Selection([
        ('quotatiom', 'Quotation'),
        ('invoice', 'Invoice'),
    ])
    allow_edit_readonly = fields.Boolean(
        default=True, compute='_compute_allow_edit_readonly')

    # OVERRIDE
    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 help="Fill this field if you plan to invoice the shipping based on picking.", default=_get_default_delivery)

    # REMOVED AFTER DB UPDATE
    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=False, index=True,
                                        help="Date on which the sales order is confirmed.", oldname="date_confirm")

    print_count = fields.Integer(string='Print Count',)
    total_purchase_price = fields.Float(compute='_compute_purchase_price', string='Total Cost')

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        for rec in self:
            rec.print_count += 1
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    @api.depends('partner_id')
    def _set_default_agent(self):
        for record in self:
            record.user_id = record.partner_id.user_id

    @api.one
    def _compute_allow_edit_readonly(self):
        is_allow_edit = False
        if self.state in ['draft', 'sent']:
            is_allow_edit = True
        else:
            is_allow_edit = False
            if self.env.user.has_group('sales_team.group_sale_manager') or self.env.user.has_group('base.group_erp_manager'):
                is_allow_edit = True

        self.allow_edit_readonly = is_allow_edit

    @api.onchange('partner_id')
    def onchange_partner_id_carrier_id(self):
        if self.partner_id:
            self.carrier_id = self.partner_id.property_delivery_carrier_id or self._get_default_delivery()

    # OVERRIDE / REMOVED AFTER DB UPDATE
    @api.multi
    def action_confirm(self):
        if not self.confirmation_date:
            raise UserError(_('Set confirmation date first!'))

        confirmation_date = self.confirmation_date
        result = super(IndySaleOrder, self).action_confirm()

        self.write({
            'confirmation_date': confirmation_date
        })

        return result
    
    @api.multi
    def action_update_cost(self):
        for record in self:
            for line in record.order_line:
                line._compute_purchase_price()

class IndySaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.model
    def _compute_purchase_price(self):
        _logger.info("OLA")
        
        frm_cur = self.env.user.company_id.currency_id
        to_cur = self.order_id.currency_id
        purchase_price = self.product_id.standard_price
        _logger.info(purchase_price)
        if self.product_uom != self.product_id.uom_id:
            purchase_price = self.product_id.uom_id._compute_price(purchase_price, self.product_uom)
        ctx = self.env.context.copy()
        ctx['date'] = self.order_id.date_order
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        _logger.info(price)
        self.write({'purchase_price': price})