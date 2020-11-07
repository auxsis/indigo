# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import xlrd

class ImportRFQWizard(models.TransientModel):
    _name = 'import.rfq.wizard'

    xls_file = fields.Binary(string="File")

    def import_rfq(self):
        row_counter = 0
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))
        for sheet in wb.sheets():
            for row in range(sheet.nrows):
                row_counter += 1
                if row_counter > 2:
                    values = {
                        'name': sheet.cell(row,0).value
                    }
                    self.env['purchase.order'].create(values)

