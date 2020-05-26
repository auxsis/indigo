from odoo import models, fields, api, _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    #date_due = fields.Date(string='Date Due')
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
            sale_order = self.env['sale.order'].search(
                [('name', '=', vals.get('origin'))], limit=1)
            if sale_order:
                vals['date_invoice'] = sale_order.confirmation_date

        result = super(AccountInvoice, self).create(vals)

        return result
