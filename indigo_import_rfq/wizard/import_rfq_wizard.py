# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
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
                    reference = sheet.cell(row,0).value
                    product_name = sheet.cell(row,4).value
                    quantity = sheet.cell(row,6).value
                    unit_price = sheet.cell(row,7).value
                    subtotal = sheet.cell(row,8).value

                    order_record = self.env['purchase.order'].search([('partner_ref', '=', reference)])
                    if not order_record:
                        order_values = {
                            # 'partner_id': 3,
                            'partner_ref': reference,
                        }
                        order_record = self.env['purchase.order'].create(order_values)

                    order_id = order_record.id

                    product_record = self.env['product.product'].search([('name', '=', product_name)])
                    if product_record:
                        product_id = product_record.id
                    else:
                        product_id = self.env['product.product'].create({'name': product_name}).id

                    order_line_values = {
                        'date_planned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'product_uom': 1,
                        'name': order_record.name,
                        'order_id': order_id,
                        'product_id': product_id,
                        'product_qty': quantity,
                        'price_unit': unit_price,
                        'price_subtotal': subtotal
                    }
                    order_line_id = self.env['purchase.order.line'].create(order_line_values)


