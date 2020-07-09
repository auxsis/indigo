# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_statement_id = fields.Many2one('bank.statement', 'Bank Statement', copy=False)
    statement_date = fields.Date('Bank.St Date', copy=False)

    @api.multi
    def write(self, vals):
        for rec in self:
            amount_residual = vals.get("amount_residual")
            if not amount_residual:
                amount_residual = rec.amount_residual
            amount_residual_currency = vals.get("amount_residual_currency")
            if not amount_residual_currency:
                amount_residual_currency = rec.amount_residual_currency
            if not vals.get("statement_date"):
                vals.update({"reconciled": False})
                if rec.currency_id and rec.amount_currency and amount_residual_currency == 0:
                    vals.update({"reconciled": True})
                if not rec.currency_id and not rec.amount_currency and amount_residual == 0:
                    vals.update({"reconciled": True})
                if rec.payment_id and rec.payment_id.state == 'reconciled':
                    rec.payment_id.state = 'posted'
            elif vals.get("statement_date"):
                vals.update({"reconciled": True})
                if rec.payment_id:
                    rec.payment_id.state = 'reconciled'
            res = super(AccountMoveLine, self).write(vals)
            return res