# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
from odoo import api, fields, models, _
import datetime
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta


class customer_statement(models.TransientModel):
    _name = "customer.statement"

    month = fields.Selection([('1', 'JAN'), ('2', 'FEB'), ('3', 'MAR'), ('4', 'APR'), ('5', 'MAY'), (
        '6', 'JUN'), ('7', 'JUL'), ('8', 'AUG'), ('9', 'SEP'), ('10', 'OCT'), ('11', 'NOV'), ('12', 'DEC')])
    aging_by = fields.Selection([('inv_date', 'Invoice Date'), (
        'due_date', 'Due Date')], string='Ageing By', default='inv_date', required="1")

    date_upto = fields.Date('Upto Date', required="1",
                            default=fields.Datetime.now)
    date_from = fields.Date('Date From', default=fields.Datetime.now)
    date_to = fields.Date('Date To')
    is_privious_year = fields.Boolean('Print Previous Year')
    as_of_date = fields.Date('As of')
    hide_paid_invoice = fields.Boolean("Hide Paid Invoices")

#     @api.onchange('month','is_privious_year')
#     def onchange_month(self):
#         if self.month:
#             a= self.month
#             a = int(a)
#             date=datetime.datetime.now()
#             if self.is_privious_year:
#                 month_end_date=datetime.datetime(date.year-1,a,1) + datetime.timedelta(days=calendar.monthrange(date.year-1,a)[1] - 1)
#                 self.date_upto = month_end_date
#             else:
#                 month_end_date=datetime.datetime(date.year,a,1) + datetime.timedelta(days=calendar.monthrange(date.year,a)[1] - 1)
#                 self.date_upto = month_end_date
    @api.onchange('is_privious_year')
    def onchange_month(self):
        if self.is_privious_year:
            self.date_to = datetime.datetime.now()
            self.date_from = date.today() + relativedelta(months=-12)

    @api.multi
    def print_statement(self):
        partner = self.env['res.partner']
        part_ids = self._context.get('active_ids')
        partner_ids = partner.browse(part_ids)
        if partner_ids:
            partner_ids.write(
                {'overdue_date': self.date_upto, 'aging_by': self.aging_by})
        datas = {
            'form': partner_ids.ids,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'as_of_date': self.as_of_date,
            'hide_paid_invoice': self.hide_paid_invoice,
        }
        return self.env.ref('dev_customer_account_statement.report_customer_statement').report_action(self, data=datas)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
