# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountReportPR(models.AbstractModel):
    _inherit = "account.aged.receivable"

    filter_analytic = False


class report_account_aged_payable(models.AbstractModel):
    _inherit = "account.aged.payable"

    filter_analytic = False


