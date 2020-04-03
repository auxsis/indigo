# -*- coding: utf-8 -*-

from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytc_account = fields.Many2one('account.analytic.account',string="Analytic Accounts")

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.sale_id:
            move_lines_ids = self.create_journal()
            mov = self.env['account.move'].create({
                'date':self.scheduled_date,
                'ref':self.name,
                'journal_id':self.product_id.categ_id.property_stock_journal.id,
                'line_ids':[(0, 0, lines) for lines in move_lines_ids]
            })
            mov.post()
            print('mov',mov)
        return res

    @api.multi
    def create_journal(self):
        res = []
        total = 0
        stock_valuation = self.env['account.account'].search([('name', 'like', 'Stock Valuation Account')]) or \
                        self.env['account.account'].search([('name', '=', 'Stock Valuation Account')])



        stock_interim = self.env['account.account'].search([('name','like','Stock Interim Account (Delivered)')]) or \
                        self.env['account.account'].search([('name','=','Stock Interim Account (Delivered)')])
        val2 = {
            'name': self.product_id.name,
            # 'price_unit': sol.price_unit,
            # 'quantity': sol.product_uom_qty,
            'price': self.sale_id.amount_total * -1,
            'debit': self.sale_id.amount_total,
            'account_id': stock_interim.id,
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'analytic_account_id': self.analytc_account.id,
            'tax_ids': self.sale_id.order_line[0].tax_id.ids,
        }
        res.append(val2)

        for sol in self.sale_id.order_line:
            for mov in self.move_lines:
                if mov.product_id.id == sol.product_id.id:
                    total = total + sol.price_subtotal
                    if(sol.tax_id):
                        val = {

                            'name': sol.product_id.name,
                            'price_unit': sol.price_unit,
                            'quantity': sol.product_uom_qty,
                            'price': sol.price_subtotal*-1,
                            'credit': sol.price_subtotal+self.sale_id.amount_tax,
                            'account_id': stock_valuation.id,
                            'product_id': sol.product_id.id,
                            'uom_id': self.product_id.uom_id.id,
                            'account_analytic_id': False,
                            'tax_ids': self.sale_id.order_line[0].tax_id.ids,
                        }
                        res.append(val)
                    else:
                        val = {

                            'name': sol.product_id.name,
                            'price_unit': sol.price_unit,
                            'quantity': sol.product_uom_qty,
                            'price': sol.price_subtotal * -1,
                            'credit': sol.price_subtotal,
                            'account_id': stock_valuation.id,
                            'product_id': sol.product_id.id,
                            'uom_id': self.product_id.uom_id.id,
                            'account_analytic_id': False,
                            'tax_ids': self.sale_id.order_line[0].tax_id.ids,
                        }
                        res.append(val)
        return res


