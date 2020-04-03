# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import deque
import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.misc import xlwt

from datetime import datetime
from datetime import date
import ast

import logging
_logger = logging.getLogger(__name__)


class SalesReportByInvoice(http.Controller):

	@http.route('/web/export_xls/sales_report_by_invoice', type='http', auth="user")
	def export_xls(self, filename, date_from, date_to, **kw):
		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Sales Report By Invoice')

		invoice_ids = request.env['account.invoice'].sudo().search([('date_invoice','>=',date_from),('date_invoice','<=',date_to)],order='date_invoice desc')

		# STYLES
		style_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: wrap no")
		style_header_right = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no")
		style_table_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz centre, vert centre, wrap on;borders: top thin, bottom thin, right thin;")
		style_table_row = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom thin, right thin;")
		style_table_row_amount = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom thin, right thin;", num_format_str="#,##0.00")
		style_table_total = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom medium, right thin;")
		style_table_total_value = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom medium, right thin;", num_format_str="#,##0.00")
		style_end_report = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz left, wrap no;")
		worksheet.col(0).width = 300*12
		worksheet.col(1).width = 300*12
		worksheet.col(2).width = 500*12
		worksheet.col(3).width = 500*12
		worksheet.col(4).width = 250*12
		worksheet.col(5).width = 250*12
		worksheet.col(6).width = 250*12
		worksheet.col(7).width = 300*12
		worksheet.col(8).width = 250*12

		# TEMPLATE HEADERS

		# TABLE HEADER
		worksheet.write(0, 0, 'CITY', style_table_header_bold) # HEADER
		worksheet.write(0, 1, 'AREA', style_table_header_bold) # HEADER
		worksheet.write(0, 2, 'SALES AGENT', style_table_header_bold) # HEADER
		worksheet.write(0, 3, "CLIENT'S NAME", style_table_header_bold) # HEADER
		worksheet.write(0, 4, 'TERMS', style_table_header_bold) # HEADER
		worksheet.write(0, 5, 'DUE DATE', style_table_header_bold) # HEADER
		worksheet.write(0, 6, 'INVOICE DATE', style_table_header_bold) # HEADER
		worksheet.write(0, 7, 'INVOICE NO.', style_table_header_bold) # HEADER
		worksheet.write(0, 8, 'AMOUNT', style_table_header_bold) # HEADER
		
		row_count = 1

		for invoice in invoice_ids:
			

			worksheet.write(row_count, 0, invoice.partner_id.city or '', style_table_row) 
			worksheet.write(row_count, 1, invoice.partner_id.partner_area_id.name  or '', style_table_row) 
			worksheet.write(row_count, 2, invoice.user_id.name  or '', style_table_row) 
			worksheet.write(row_count, 3, invoice.partner_id.name  or '', style_table_row) 
			worksheet.write(row_count, 4, invoice.payment_term_id.name or '', style_table_row) 
			worksheet.write(row_count, 5, invoice.date_due or '', style_table_row) 
			worksheet.write(row_count, 6, invoice.date_invoice  or '', style_table_row) 
			worksheet.write(row_count, 7, invoice.number  or '', style_table_row) 
			worksheet.write(row_count, 8, invoice.amount_total  or '', style_table_row_amount) 
			row_count +=1
	   

		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', 'attachment; filename=%s;'%(filename)
					)])

		workbook.save(response.stream)

		return response
