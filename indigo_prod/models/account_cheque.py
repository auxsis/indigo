from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AccountCheque(models.Model):
    _inherit = "account.cheque"
    
    # NEW FIELDS
    bank_id = fields.Many2one('res.bank', string='Bank')
    bank_account_number_id = fields.Many2one('res.partner.bank', string='Bank Account Number')
    
    # OVERRIDE
    name = fields.Char(string="Name", required=False, related='sequence')
    
    @api.onchange('sequence')
    def set_name(self):
        self.name = self.sequence
        
    # UNPOST ENTRIES / UNRECONCILE
    @api.multi
    def unpost_cheque_entries(self):
        for record in self:
            account_move_ids = self.env['account.move'].search([('account_cheque_id','=',record.id)])
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
            account_move_ids = self.env['account.move'].search([('account_cheque_id','=',record.id)])
            for move in account_move_ids:
                if move.state == 'draft':
                    move.post()
                    
                    
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
