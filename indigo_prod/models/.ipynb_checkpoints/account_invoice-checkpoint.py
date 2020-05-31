from odoo import models, fields, api, _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    def _is_convert_currency(self):
        convert_currency = False
        if self.company_id and self.currency_id:
            if self.company_id.currency_id != self.currency_id:
                convert_currency = True
        self.convert_currency = convert_currency
    
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
                self.due_date = fields.Date.from_string(
                    rec.date_due).strftime('%m/%d/%Y')
            else:
                self.due_date = fields.Date.from_string(
                    rec.date_invoice).strftime('%m/%d/%Y')
        self.action_invoice_open()
    
    # OVERRIDE TO SET INVOICE DATE BASED ON SALES CONFIRMATION DATE / TO BE REMOVED AFTER DATA ENCODING
    @api.model
    def create(self, vals):
        if vals.get('origin'):
            sale_order = self.env['sale.order'].search([('name','=',vals.get('origin'))], limit=1)
            if sale_order:
                vals['date_invoice'] = sale_order.confirmation_date
        
        result = super(AccountInvoice, self).create(vals)
        
        return result
    
    @api.onchange('currency_id')
    def _get_currency_rate(self):
        self._is_convert_currency()
        self.exchange_rate = self.currency_id.rate
        
    def action_view_customer_statement(self):
    # return self.partner_id.open_action_followup()
        self.ensure_one()
        ctx = self.env.context.copy()
        # partners_data = self.get_partners_in_need_of_action_and_update()
        _logger.info("HALO")
        _logger.info(self._context.get('active_ids'))
        partners_data = self.partner_id.get_partners_in_customer_statement_list(self.ids)
        ctx = self.env.context.copy()
        ctx.update({
            'model': 'account.followup.report', 
            'lang': self.partner_id.lang,
            'followup_line_id': partners_data.get(self.id) and partners_data[self.id][0] or False,
        })
        return {
                'type': 'ir.actions.client',
                'tag': 'account_report_followup',
                'context': ctx,
                'options': {'partner_id': self.partner_id.id},
            }
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    orig_price_unit = fields.Float(string='Original Currency Price')
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice','invoice_id.exchange_rate')
    def _compute_price(self):
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type
        exchange_rate = self.invoice_id.exchange_rate
        
        price_unit = self.product_id.standard_price
        orig_price_unit = self.product_id.standard_price
        if self.purchase_line_id:
            orig_price_unit = self.purchase_line_id.price_unit
            price_unit = self.purchase_line_id.price_unit
            
        if self.product_id and type in ('in_invoice', 'in_refund'):
            if company and currency:
                if company.currency_id != currency and exchange_rate:
                    price_unit = price_unit * exchange_rate
        self.price_unit = price_unit
        self.orig_price_unit = orig_price_unit
        result = super(AccountInvoiceLine, self)._compute_price()
        return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        result = super(AccountInvoiceLine, self)._onchange_product_id()
        
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type
        exchange_rate = self.invoice_id.exchange_rate
        
        orig_price_unit = self.product_id.standard_price
        price_unit = self.product_id.standard_price
        
        if self.purchase_line_id:
            orig_price_unit = self.purchase_line_id.price_unit
            price_unit = self.purchase_line_id.price_unit
         
        if self.product_id and type in ('in_invoice', 'in_refund'):
            if company and currency:
                if company.currency_id != currency and exchange_rate:
                    price_unit = price_unit * exchange_rate
                    
        self.price_unit = price_unit
        self.orig_price_unit = orig_price_unit
        return result