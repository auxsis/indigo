# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import time
import xlrd

from collections import OrderedDict
from datetime import datetime

from odoo import api, fields, models


class PurchaseOrderImport(models.TransientModel):
    _name = 'purchase.order.import'
    _description = 'Purchase Order Import'

    file = fields.Binary('File', required=True)

    def get_data(self, keys, sheet):
        for i in range(1, sheet.nrows):
            row = (c.value for c in sheet.row(i))
            yield OrderedDict(zip(keys, row))

    def import_purchase_order(self):
        xlDecoded = base64.b64decode(self.file)
        xlsx = xlrd.open_workbook(file_contents=xlDecoded)
        sheet = xlsx.sheet_by_index(0)
        keys = [c.value for c in sheet.row(0)]
        data = self.get_data(keys, sheet)
        vendor = False
        company = False
        order_line = []
        for rec in data:
            if rec.get('VENDOR') and not vendor:
                vendor = self.env['res.partner'].search([('name', '=', rec.get('VENDOR'))])
            if rec.get('COMPANY NAME') and not company:
                company = self.env['res.company'].search([('name', '=', rec.get('COMPANY NAME'))])
            if not vendor:
                return
            product = self.env['product.product'].search([('default_code', '=', rec.get('ITEM NO.'))])
            if product:
                order_line.append((0, 0, {
                    'product_id': product.id,
                    'name': rec.get('DESCRIPTION'),
                    'product_qty': rec.get("Q'TY"),
                    'price_unit': rec.get('PRICE'),
                    'date_planned': fields.Datetime.now(),
                    'product_uom': product.uom_id.id,
                    'ctns': rec['CTNS'],
                    'tgw': rec['T.G.W.'],
                    'tnw': rec['T.N.W.'],
                    'total_volume': rec['TOTAL VOLUME'],
                    'pcs_ctn': rec['PCS/CTN'],
                    'length': rec['L'],
                    'weight': rec['W'],
                    'height': rec['H'],
                    'gw': rec['G.W.'],
                    'nw': rec['N.W.'],
                }))
        vals = {
            'partner_id': vendor.id,
            'company_id': company and company.id or self.env.user.company_id.id,
            'order_line': order_line,
            'name': rec.get('P/I NO.')
        }
        self.env['purchase.order'].create(vals)
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def action_import_purchase_order(self):
        view_id = self.env.ref('purchase_import.view_purchase_order_import_form').id
        return {
            'name': 'Import Purchase Order',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }
