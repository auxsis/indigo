from odoo import models, fields, api, _
from num2words import num2words

from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    # NEW FIELDS
    bank_id = fields.Many2one('res.bank', string='Bank')
    bank_account_number_id = fields.Many2one(
        'res.partner.bank', string='Bank Account Number')
    check_amount_in_words = fields.Char(string="Amount in Words")
    deposit_date = fields.Date(string="Deposit Date")
    bounced_date = fields.Date(string="Bounced Cheque Date")
    bounced_count = fields.Integer(string="Bounced Cheque Count")
    returned_date = fields.Date(string="Returned Date")
    returned_count = fields.Integer(string="Returned Count")
    applied_invoice_ids = fields.Many2many('account.invoice', string="Applied Invoices", compute="_compute_account_applied_invoice")

    # OVERRIDE FIELD
    status1 = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('deposited', 'Deposited'),
        ('bounced', 'Bounced'),
        ('return', 'Returned'),
        ('transfered', 'Transfered'),
        ('closed', 'Closed'),
        ('cashed', 'Done'),
        ('cancel', 'Cancel')
    ], string="Status", default="draft", copy=False, index=True, track_visibility='onchange')

    @api.onchange('bank_account_id')
    def _onchange_bank_account_id(self):
        bank_number = self.env['account.journal'].search(
            [('default_debit_account_id', '=', self.bank_account_id.id)])

        if bank_number:
            self.bank_account_number_id = bank_number[0].bank_account_id.id
            #self.bank_id = bank_number[0].bank_id.id
        else:
            self.bank_account_number_id = None
            #self.bank_id = None

    @api.multi
    def update_bank_id(self):
        for record in self:
            record._onchange_bank_account_id()
        return True

    # @api.onchange('bank_id')
    # def _onchange_bank_id(self):
    #    bank_number = self.env['res.partner.bank'].search(
    #        [('bank_id', '=', self.bank_id.id)])

    #    if bank_number:
    #        self.bank_account_number_id = bank_number[0].id
    #    else:
    #        self.bank_account_number_id = False
    # OVERRIDE
    name = fields.Char(string="Name", required=False, related='sequence')

    @api.onchange('amount')
    def _onchange_amount(self):
        whole = num2words(int(self.amount)) + ' Pesos '
        whole = whole.replace(' and ', ' ')
        if "." in str(self.amount):  # quick check if it is decimal
            decimal_no = str(round(self.amount, 2)).split(".")[1]
            if len(decimal_no) == 1:
                decimal_no = decimal_no + "0"
            if decimal_no:
                whole = whole + "and " + decimal_no + '/100'
        whole = whole.replace(',', '')
        self.check_amount_in_words = whole.upper() + " ONLY"

    @api.onchange('sequence')
    def set_name(self):
        self.name = self.sequence

    # CLOSED
    @api.multi
    def set_to_close(self):
        if self.account_cheque_type == 'incoming':
            account_move_obj = self.env['account.move']
            account_move = account_move_obj.search(
                [('account_cheque_id', '=', self.id)])
            account_move.button_cancel()
            account_move.unlink()
            self.status1 = 'closed'
        return account_move

    # UNPOST ENTRIES / UNRECONCILE
    @api.multi
    def unpost_cheque_entries(self):
        for record in self:
            account_move_ids = self.env['account.move'].search(
                [('account_cheque_id', '=', record.id)])
            for move in account_move_ids:
                if move.state == 'posted':
                    for line in move.line_ids:
                        if line.matched_debit_ids:
                            for debit in line.matched_debit_ids:
                                debit.debit_move_id.remove_move_reconcile()
                        if line.matched_credit_ids:
                            for credit in line.matched_debit_ids:
                                credit.credit_move_id.remove_move_reconcile()
                        line.remove_move_reconcile()
                    move.button_cancel()

    # UNPOST ENTRIES / UNRECONCILE
    @api.multi
    def post_cheque_entries(self):
        for record in self:
            account_move_ids = self.env['account.move'].search(
                [('account_cheque_id', '=', record.id)])
            for move in account_move_ids:
                if move.state == 'draft':
                    move.post()

    # INHERIT DEPOSITE FUNCTION
    @api.multi
    def set_to_deposite(self):
        if not self.deposit_date:
            raise UserError(_('Deposit Date is required!'))
        result = super(AccountCheque, self).set_to_deposite()
        return result

    # INHERIT BOUNCED FUNCTION
    @api.multi
    def set_to_bounced(self):
        if not self.bounced_date:
            raise UserError(_('Bounced Cheque Date is required!'))
        result = super(AccountCheque, self).set_to_bounced()
        self.bounced_count += 1
        return result

    # INHERIT RETURN FUNCTION
    @api.multi
    def set_to_return(self):
        if not self.returned_date:
            raise UserError(_('Returned Date is required!'))
        result = super(AccountCheque, self).set_to_return()
        self.returned_count += 1
        return result

    # FOR SCRIPT USE
    @api.multi
    def update_amount_words(self):
        for record in self:
            record._onchange_amount()
        return True

    @api.multi
    def update_bank_account_number(self):
        for record in self:
            record._onchange_bank_account_id()
        return True

    # OVERRIDE
#     def open_payment_matching_screen(self):
#         _logger.info("OLA")
#         # Open reconciliation view for customers/suppliers
#         move_line_id = False
#         account_move_ids = self.env['account.move'].search([('account_cheque_id','=',self.id)])
#         account_move_line_ids = account_move_ids.mapped('line_ids')
#         for move_line in account_move_line_ids:
#             if move_line.account_id.reconcile:
#                 move_line_id = move_line.id
#                 break;
#         action_context = {'company_ids': [self.company_id.id], 'partner_ids': [self.payee_user_id.id]}
#         if self.account_cheque_type == 'incoming':
#             action_context.update({'mode': 'customers'})
#         elif self.account_cheque_type == 'outgoing':
#             action_context.update({'mode': 'suppliers'})
#         if account_move_line_ids:
#             action_context.update({'move_line_id': move_line_id})
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'manual_reconciliation_view',
#             'context': action_context,
#         }

    @api.multi
    def _compute_account_applied_invoice(self):
        for record in self:
            invoice_list = []
            move_ids = self.env['account.move'].search([('account_cheque_id', '=', record.id)])
            for move in move_ids:
                for line in move.line_ids:
                    if line.full_reconcile_id:
                        invoice_ids = line.full_reconcile_id.mapped('reconciled_line_ids').mapped('invoice_id').ids
                        for invoice in invoice_ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
                    if line.matched_credit_ids:
                        invoice_ids = line.matched_credit_ids.mapped('credit_move_id').mapped('invoice_id').ids
                        for invoice in invoice_ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
                    if line.matched_debit_ids:
                        invoice_ids = line.matched_debit_ids.mapped('debit_move_id').mapped('invoice_id').ids
                        for invoice in invoice_ids:
                            if invoice not in invoice_list:
                                invoice_list.append(invoice)
            record.applied_invoice_ids = [(6, 0, invoice_list)]
        return
