# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SalesOrderDeletePosted(models.TransientModel):
    _name = "sale.order.delete.posted"
    _description = "Delete Sales Order Already Posted"
    
    def delete_sales_order(self):
        sale_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
        for sale in sale_ids:
            invoice_ids = sale.mapped('invoice_ids')
            picking_ids = sale.mapped('picking_ids')
            if picking_ids:
                for picking in picking_ids:
                    move_lines = picking.move_lines
                    for move in move_lines:
                        move_line_ids = move.move_line_ids
                        move_update = move.write({'state':'draft'})
                        if move_update:
                            for line in move_line_ids:
                                line.unlink()
                            # move.write({'state':'draft'})
                        move.unlink()
                    picking.unlink()
                    
            if invoice_ids:
                for invoice in invoice_ids:
                    account_move = invoice.move_id
                    payment_ids = invoice.payment_ids
                    payment_move_line_ids = invoice.payment_move_line_ids
                    
                    # JOURNAL ENTRIES
                    if account_move and account_move.state != 'draft':
                        account_move.button_cancel()
                    
                    # PAYMENTS
                    if payment_move_line_ids:
                        for line in payment_move_line_ids:
                            line.remove_move_reconcile()
                    if payment_ids:
                        for payment in payment_ids:
                            payment_invoice_ids = payment.invoice_ids
                            if payment.state in ['draft','cancelled']:
                                payment.write({'move_name':''})
                            else:
                                if payment_invoice_ids:
                                    payment_move = []
                                    for line in payment.move_line_ids:
                                        payment_unreconcile = line.remove_move_reconcile()
                                        if payment_unreconcile and line.move_id not in payment_move:
                                            payment_move.append(line.move_id)
                                            
                                    for move in payment_move:
                                        move.button_cancel()
                                        move.unlink()
                            payment.write({'state':'cancelled','move_name':''})
                            payment.unlink()
                    if invoice.state in ['draft','open']:
                        invoice_cancel = invoice.action_invoice_cancel()
                        if invoice_cancel:
                            invoice.write({'move_name':''})
                        invoice.unlink()
                    else:
                        invoice.unlink()
                        
            sale.action_cancel()
            sale.unlink()
        return True