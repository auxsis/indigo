from odoo import models, fields, api, _ 

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
                        line.remove_move_reconcile()
                    move.button_cancel()
