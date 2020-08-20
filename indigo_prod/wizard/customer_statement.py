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
import calendar
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class CustomerStatementMonthly(models.TransientModel):
    _name = "customer.statement.monthly"

    month = fields.Selection([('1', 'JANUARY'), ('2', 'FEBRUARY'), ('3', 'MARCH'), ('4', 'APRIL'), ('5', 'MAY'), (
        '6', 'JUNE'), ('7', 'JULY'), ('8', 'AUGUST'), ('9', 'SEPTEMBER'), ('10', 'OCTOBER'), ('11', 'NOVEMBER'), ('12', 'DECEMBER')], required=True)
    year = fields.Selection([(num, str(num)) for num in range(1999, (datetime.now().year)+1 )], string='Year', required=True)
    aging_by = fields.Selection([('inv_date', 'Invoice Date'), ('due_date', 'Due Date')], string='Ageing By', default='inv_date', required="1")

#     date_upto = fields.Date('Upto Date', required="1",default=fields.Datetime.now)
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    is_privious_year = fields.Boolean('Print Previous Year')
    as_of_date = fields.Date('As of')

    @api.onchange('month','year')
    def onchange_month_year(self):
        if self.month and self.year:
            month = int(self.month)
            date = datetime.now()
            date_from = datetime(year=self.year, month=month, day=1)
            date_to = datetime(year=self.year, month=month, day=1) + timedelta(days=calendar.monthrange(self.year,month)[1] - 1)

            self.date_from = date_from
            self.date_to = date_to
                
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
                {'overdue_date': self.date_to, 'aging_by': self.aging_by})
        datas = {
            'form': partner_ids.ids,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'as_of_date': self.as_of_date,
        }
        return self.env.ref('dev_customer_account_statement.report_customer_statement').report_action(self, data=datas)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
