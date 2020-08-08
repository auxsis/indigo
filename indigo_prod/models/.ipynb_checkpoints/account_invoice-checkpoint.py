from odoo import models, fields, api, _
from datetime import datetime
import math

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _is_convert_currency(self):
        convert_currency = False
        if self.purchase_currency_id and self.currency_id:
            if self.purchase_currency_id != self.currency_id:
                convert_currency = True
        else:
            if self.purchase_id:
                if self.purchase_id.currency_id != self.purchase_id.company_id.currency_id:
                    convert_currency = True
        self.convert_currency = convert_currency

    purchase_currency_id = fields.Many2one(
        'res.currency', string='Purchase Currency')
    exchange_rate = fields.Float(string='Exchange Rate')
    convert_currency = fields.Boolean(compute='_is_convert_currency')
    due_date = fields.Char(string="Date Due", strore=True)

    @api.onchange('date_due')
    def _convert_date(self):
        for record in self:
            if record.date_due:
                record.due_date = fields.Date.from_string(
                    record.date_due).strftime('%m/%d/%Y')
            else:
                record.due_date = '0'  # datetime.now().strftime('%m/%d/%Y')

    @api.multi
    def action_invoice_open2(self):
        for rec in self:
            if rec.date_due:
                rec.due_date = fields.Date.from_string(
                    rec.date_due).strftime('%m/%d/%Y')
            else:
                if rec.date_invoice:
                    rec.due_date = fields.Date.from_string(
                        rec.date_invoice).strftime('%m/%d/%Y')
            rec.action_invoice_open()

    # OVERRIDE TO SET INVOICE DATE BASED ON SALES CONFIRMATION DATE / TO BE REMOVED AFTER DATA ENCODING
    @api.model
    def create(self, vals):
        if vals.get('origin'):
            sale_order = self.env['sale.order'].search(
                [('name', '=', vals.get('origin'))], limit=1)
            if sale_order:
                vals['date_invoice'] = sale_order.confirmation_date

        result = super(AccountInvoice, self).create(vals)

        return result

    @api.onchange('purchase_currency_id')
    def _get_currency_rate(self):
        self._is_convert_currency()
        self.exchange_rate = self.purchase_currency_id.rate

    @api.multi
    def action_view_customer_statement(self):
        # return self.partner_id.open_action_followup()
        # self.ensure_one()
        partner_id = False
        invoice_ids = self._context.get('active_ids', [])
        for record in self:
            if not partner_id:
                partner_id = record.partner_id

        if partner_id:
            partners_data = partner_id.get_partners_in_customer_statement_list(
                invoice_ids)
            context = self.env.context.copy()
            context.update({
                'model': 'account.followup.report',
                'lang': partner_id.lang,
                'followup_line_id': partners_data.get(partner_id.id) and partners_data[partner_id.id][0] or False,
                'invoice_ids': invoice_ids,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'account_report_followup',
                'context': context,
                'options': {'partner_id': partner_id.id},
            }

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_currency_id:
            self.purchase_currency_id = self.purchase_id.currency_id
        result = super(AccountInvoice, self).purchase_order_change()
        self._is_convert_currency()
        return result

#     @api.multi
#     def action_invoice_open(self):
#         for record in self:
#             if record.type in ['in_invoice','in_refund'] and not record.date_invoice:
#                 raise UserError(_("Please input bill date before you validate the vendor bill."))

#         result = super(AccountInvoice, self).action_invoice_open()

#         return result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    orig_price_unit = fields.Float(string='Original Currency Price')

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.exchange_rate', 'invoice_id.purchase_currency_id')
    def _compute_price(self):
        if self.invoice_id.convert_currency:
            # company = self.invoice_id.company_id
            purchase_currency_id = self.invoice_id.purchase_currency_id
            currency = self.invoice_id.currency_id
            type = self.invoice_id.type
            exchange_rate = self.invoice_id.exchange_rate

            price_unit = self.product_id.standard_price
            orig_price_unit = self.product_id.standard_price
            if self.purchase_line_id:
                orig_price_unit = self.purchase_line_id.price_unit
                price_unit = self.purchase_line_id.price_unit

            if self.product_id and type in ('in_invoice', 'in_refund'):
                if purchase_currency_id and currency:
                    if purchase_currency_id != currency and exchange_rate:
                        price_unit = price_unit * exchange_rate
#                         _logger.info([math.floor(price_unit * 10 ** i) / 10 ** i for i in range(3)])
                        price_unit = [math.floor(price_unit * 10 ** i) / 10 ** i for i in range(3)][2]
            self.price_unit = price_unit
            self.orig_price_unit = orig_price_unit
        result = super(AccountInvoiceLine, self)._compute_price()
        return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        result = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.convert_currency:
            # company = self.invoice_id.company_id
            purchase_currency_id = self.invoice_id.purchase_currency_id
            currency = self.invoice_id.currency_id
            type = self.invoice_id.type
            exchange_rate = self.invoice_id.exchange_rate

            orig_price_unit = self.product_id.standard_price
            price_unit = self.product_id.standard_price

            if self.purchase_line_id:
                orig_price_unit = self.purchase_line_id.price_unit
                price_unit = self.purchase_line_id.price_unit

            if self.product_id and type in ('in_invoice', 'in_refund'):
                if purchase_currency_id and currency:
                    if purchase_currency_id != currency and exchange_rate:
                        price_unit = [math.floor(price_unit * 10 ** i) / 10 ** i for i in range(3)][2]

            self.price_unit = price_unit
            self.orig_price_unit = orig_price_unit
        return result
