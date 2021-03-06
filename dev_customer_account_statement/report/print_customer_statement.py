# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime
import dateutil.relativedelta
from datetime import timedelta
import calendar
from odoo.tools.misc import formatLang


class print_customer_statement(models.AbstractModel):
    _name = 'report.dev_customer_account_statement.cust_statement_template'

    @api.multi
    def set_amount(self, amount):
        amount = formatLang(self.env, amount)
        return amount

    def get_month_name(self, day, mon, year):
        year = str(year)
        day = str(day)
        if mon == 1:
            return day + ' - ' + 'JAN'+' - '+year
        elif mon == 2:
            return day + ' - ' + 'FEB'+' - '+year
        elif mon == 3:
            return day + ' - ' + 'MAR'+' - '+year
        elif mon == 4:
            return day + ' - ' + 'APR'+' - '+year
        elif mon == 5:
            return day + ' - ' + 'MAY'+' - '+year
        elif mon == 6:
            return day + ' - ' + 'JUN'+' - '+year
        elif mon == 7:
            return day + ' - ' + 'JUL'+' - '+year
        elif mon == 8:
            return day + ' - ' + 'AUG'+' - '+year
        elif mon == 9:
            return day + ' - ' + 'SEP'+' - '+year
        elif mon == 10:
            return day + ' - ' + 'OCT'+' - '+year
        elif mon == 11:
            return day + ' - ' + 'NOV'+' - '+year
        elif mon == 12:
            return day + ' - ' + 'DEC'+' - '+year

    def set_ageing(self, obj):
        move_lines = self.get_lines(obj)

        over_date = datetime.strptime(obj.overdue_date, "%Y-%m-%d")
        d1 = over_date - dateutil.relativedelta.relativedelta(months=1)
        d1 = datetime(d1.year, d1.month, 1) + \
            timedelta(days=calendar.monthrange(d1.year, d1.month)[1] - 1)
        d2 = over_date - dateutil.relativedelta.relativedelta(months=2)
        d2 = datetime(d2.year, d2.month, 1) + \
            timedelta(days=calendar.monthrange(d2.year, d2.month)[1] - 1)
        d3 = over_date - dateutil.relativedelta.relativedelta(months=3)
        d3 = datetime(d3.year, d3.month, 1) + \
            timedelta(days=calendar.monthrange(d3.year, d3.month)[1] - 1)
        d4 = over_date - dateutil.relativedelta.relativedelta(months=4)
        d4 = datetime(d4.year, d4.month, 1) + \
            timedelta(days=calendar.monthrange(d4.year, d4.month)[1] - 1)
        d5 = over_date - dateutil.relativedelta.relativedelta(months=5)
        d5 = datetime(d5.year, d5.month, 1) + \
            timedelta(days=calendar.monthrange(d5.year, d5.month)[1] - 1)

        con1 = int(str(over_date - d1).split(' ')[0])
        con2 = int(str(over_date - d2).split(' ')[0])
        con3 = int(str(over_date - d3).split(' ')[0])
        con4 = int(str(over_date - d4).split(' ')[0])
        con5 = int(str(over_date - d5).split(' ')[0])

        f1 = self.get_month_name(
            over_date.day, over_date.month, over_date.year)
        d1 = self.get_month_name(d1.day, d1.month, d1.year)
        d2 = self.get_month_name(d2.day, d2.month, d2.year)
        d3 = self.get_month_name(d3.day, d3.month, d3.year)
        d4 = self.get_month_name(d4.day, d4.month, d4.year) + ' (UPTO)'
        d5 = self.get_month_name(d5.day, d5.month, d5.year)

        not_due = 0.0
        f_pe = 0.0  # 0 -30
        s_pe = 0.0  # 31-60
        t_pe = 0.0  # 61-90
        fo_pe = 0.0  # 91-120
        l_pe = 0.0  # +120
        for line in move_lines:
            ag_date = False
            if obj.aging_by == 'due_date':
                ag_date = line.get('date_maturity')
            else:
                ag_date = line.get('date')
            if ag_date and obj.overdue_date:
                due_date = datetime.strptime(ag_date, "%Y-%m-%d")
                over_date = datetime.strptime(obj.overdue_date, "%Y-%m-%d")
                if over_date != due_date:
                    if not ag_date > obj.overdue_date:
                        days = over_date - due_date
                        days = int(str(days).split(' ')[0])
                    else:
                        days = -1
                else:
                    days = 0

                if days < 0:
                    not_due += line.get('total')
                elif days < con1:
                    f_pe += line.get('total')
                elif days < con2:
                    s_pe += line.get('total')
                elif days < con3:
                    t_pe += line.get('total')
                elif days < con4:
                    fo_pe += line.get('total')
                else:
                    l_pe += line.get('total')

        return [{
                'not_due': not_due,
                f1: f_pe,
                d1: s_pe,
                d2: t_pe,
                d3: fo_pe,
                d4: l_pe,
                }, [f1, d1, d2, d3, d4]]

    def _lines_get(self, partner, date_from, date_to):
        moveline_obj = self.env['account.move.line']
        domain = [('partner_id', '=', partner.id), ('account_id.user_type_id.type',
                                                    '=', 'receivable'), ('move_id.state', '=', 'posted')]
        if partner.aging_by == 'inv_date':
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        if partner.aging_by == 'due_date':
            domain += [('date', '>=', date_from),
                       ('date', '<=', date_to)]
        movelines = moveline_obj.search(domain)

        return movelines

    def get_lines(self, partner, date_from, date_to):
        move_lines = self._lines_get(partner, date_from, date_to)
        res = []
        if move_lines:
            for line in move_lines:
                inv_amt = 0.0
                paid_amt = 0.0
                if line.account_id.user_type_id.type == 'receivable':
                    if line.debit:
                        inv_amt = line.debit
                    else:
                        inv_amt = line.credit * -1
                total = 0.0
                if inv_amt > 0:
                    for m in line.matched_credit_ids:
                        c_date = datetime.strptime(
                            m.credit_move_id.date, "%Y-%m-%d")
                        part_over_date = datetime.strptime(
                            partner.overdue_date, "%Y-%m-%d")
                        if c_date <= part_over_date:
                            paid_amt += m.amount
                else:
                    for m in line.matched_debit_ids:
                        c_date = datetime.strptime(
                            m.debit_move_id.date, "%Y-%m-%d")
                        part_over_date = datetime.strptime(
                            partner.overdue_date, "%Y-%m-%d")
                        if c_date <= part_over_date:
                            paid_amt += (m.amount * -1)

                total = float(inv_amt - paid_amt)
                if total > 0 or total < 0:
                    res.append({
                        'date': line.date,
                        'desc': line.ref or '/',
                        'ref': line.move_id.name or '',
                        'legacy_number': line.invoice_id.legacy_number,
                        'origin': line.invoice_id.origin,
                        'date_maturity': line.date_maturity,
                        'debit': float(inv_amt),
                        'credit': float(paid_amt),
                        'total': float(total),
                    })
            if res:
                res.sort(key=lambda rec: rec.get('date'))
        return res

    def _lines_get_all_invoice(self, partner, date_from, date_to):
        inv_obj = self.env['account.invoice']
        domain = [('partner_id', '=', partner.id),
                  ('state', 'in', ['open', 'paid'])]
        if partner.aging_by == 'inv_date':
            domain += [('date_invoice', '>=', date_from),
                       ('date_invoice', '<=', date_to)]
        if partner.aging_by == 'due_date':
            domain += [('date_invoice', '>=', date_from),
                       ('date_invoice', '<=', date_to)]
        invoices = inv_obj.search(domain)

        return invoices

    def get_lines_all_invoice(self, partner, date_from, date_to):
        invoices = self._lines_get_all_invoice(partner, date_from, date_to)
        res = []
        if invoices:
            for inv in invoices:
                inv_amt = inv.amount_total_signed
                paid_amt = 0.0

                if inv:
                    for line in inv.payment_move_line_ids:
                        if line.account_id.user_type_id.type == 'receivable':
                            if line.debit:
                                paid_amt += (line.debit * -1)
                            else:
                                paid_amt += line.credit

                total = float(inv_amt - paid_amt)
                res.append({
                    'date': inv.date_invoice,
                    'ref': inv.name or '',
                    'legacy_number': inv.legacy_number,
                    'origin': inv.origin,
                    'date_maturity': inv.date_due,
                    'debit': float(inv_amt),
                    'credit': float(paid_amt),
                    'total': float(total),
                })

        return res

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'res.partner',
            'docs': docs,
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'as_of_date': data['as_of_date'],
            'get_lines': self.get_lines,
            'get_lines_all_invoice': self.get_lines_all_invoice,
            'set_ageing': self.set_ageing,
            'set_amount': self.set_amount,
            'hide_paid_invoice': data['hide_paid_invoice'],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
