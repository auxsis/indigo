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


class ExportSaleOutstockItemReport(http.Controller):

	@http.route('/web/export_xls/sale_outstock_item', type='http', auth="user")
	def export_xls(self, filename, sale_ids, date_from, date_to, is_admin, **kw):
		is_admin = ast.literal_eval(is_admin)

		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Sales Out of Stock Items')

		sale_order_ids = False

		sales = request.env['sale.order'].sudo().search([('id','in',ast.literal_eval(sale_ids))])
		if sales:
			sale_order_ids = sales
		
		if not sales:
			# sale_order_ids = request.env['sale.order'].search([('id','in',ast.literal_eval(sale_ids))])
			sales_date = request.env['sale.order'].sudo().search([('date_order','>=',date_from),('date_order','<=',date_to)],order='date_order desc')
			if sales_date:
				sale_order_ids = sales_date
		

		# STYLES
		style_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: wrap no")
		style_header_right = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no")
		style_table_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz centre, vert centre, wrap on;borders: top thin, bottom thin, right thin;")
		style_table_row = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom thin, right thin;")
		style_table_row_amount = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom thin, right thin;", num_format_str="#,##0.00")
		style_table_total = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom medium, right thin;")
		style_table_total_value = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom medium, right thin;", num_format_str="#,##0.00")
		style_end_report = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz left, wrap no;")
		worksheet.col(0).width = 250*12
		worksheet.col(1).width = 500*12
		worksheet.col(2).width = 250*12
		worksheet.col(3).width = 250*12
		worksheet.col(4).width = 250*12
		worksheet.col(5).width = 250*12
		worksheet.col(6).width = 250*12
		worksheet.col(7).width = 250*12
		worksheet.col(8).width = 250*12
		worksheet.col(9).width = 250*12
		worksheet.col(10).width = 250*12
		worksheet.col(11).width = 250*12
		worksheet.col(12).width = 250*12
		worksheet.col(13).width = 250*12
		worksheet.col(14).width = 250*12
		worksheet.col(15).width = 250*12
		worksheet.col(16).width = 250*12
		worksheet.col(17).width = 250*12

		# TEMPLATE HEADERS

		# TABLE HEADER
		worksheet.write(0, 0, 'Sales Agent', style_table_header_bold) # HEADER
		worksheet.write(0, 1, "Client's Name", style_table_header_bold) # HEADER
		worksheet.write(0, 2, 'City', style_table_header_bold) # HEADER
		worksheet.write(0, 3, 'Area', style_table_header_bold) # HEADER
		worksheet.write(0, 4, 'Invoice Date', style_table_header_bold) # HEADER
		worksheet.write(0, 5, 'Invoice No.', style_table_header_bold) # HEADER
		# worksheet.write(0, 6, 'Category', style_table_header_bold) # HEADER
		worksheet.write(0, 6, 'Item Code', style_table_header_bold) # HEADER
		worksheet.write(0, 7, 'Description', style_table_header_bold) # HEADER
		worksheet.write(0, 8, 'Color', style_table_header_bold) # HEADER
		worksheet.write(0, 9, 'Brand', style_table_header_bold) # HEADER
		worksheet.write(0, 10, 'Car Brand', style_table_header_bold) # HEADER
		worksheet.write(0, 11, 'Model', style_table_header_bold) # HEADER
		worksheet.write(0, 12, 'Car Model Group 1', style_table_header_bold) # HEADER
		worksheet.write(0, 13, 'Car Model Group 2', style_table_header_bold) # HEADER
		worksheet.write(0, 14, 'Car Model Group 3', style_table_header_bold) # HEADER
		worksheet.write(0, 15, 'Car Type', style_table_header_bold) # HEADER
		worksheet.write(0, 16, 'Fit', style_table_header_bold) # HEADER
		worksheet.write(0, 17, 'Parent Category', style_table_header_bold) # HEADER
		worksheet.write(0, 18, 'Category', style_table_header_bold) # HEADER
		worksheet.write(0, 19, 'Qty', style_table_header_bold) # HEADER
		worksheet.write(0, 20, 'Unit Price', style_table_header_bold) # HEADER
		worksheet.write(0, 21, 'Amount', style_table_header_bold) # HEADER
		worksheet.write(0, 22, 'Discount (%)', style_table_header_bold) # HEADER
		worksheet.write(0, 23, 'Net Sales', style_table_header_bold) # HEADER
		if is_admin == True:
			_logger.info("TRUE")
			worksheet.write(0, 24, 'Foreign Cost', style_table_header_bold) # HEADER
			worksheet.write(0, 25, 'Exchange Rate', style_table_header_bold) # HEADER
			worksheet.write(0, 26, 'Local Cost', style_table_header_bold) # HEADER
			worksheet.write(0, 27, 'Remarks', style_table_header_bold) # HEADER
		else:
			_logger.info("FALSE")
			worksheet.write(0, 24, 'Remarks', style_table_header_bold) # HEADER

		row_count = 1

		for sale in sale_order_ids:
			for line in sale.order_line:
				invoice_id = ''
				# for invoice in line.invoice_lines:
				# 	invoice_date = str(invoice.date)
				# 	invoice_no = str(invoice.name)
				# invoice_id = line.mapped('invoice_lines').mapped('invoice_id')
				for invoice in line.invoice_lines:
					invoice_id = invoice.invoice_id.id

				invoice_date = False
				invoice_no = ''
				if invoice_id:
					invoice = request.env['account.invoice'].sudo().search([('id','=',invoice_id)])
					invoice_date = invoice.date_invoice
					invoice_no = invoice.number


				worksheet.write(row_count, 0, sale.user_id.name or '', style_table_row) 
				worksheet.write(row_count, 1, sale.partner_id.name  or '', style_table_row) 
				worksheet.write(row_count, 2, sale.partner_id.city  or '', style_table_row) 
				worksheet.write(row_count, 3, sale.partner_id.partner_area_id.name  or '', style_table_row) 
				worksheet.write(row_count, 4, invoice_date or '', style_table_row) 
				worksheet.write(row_count, 5, invoice_no or '', style_table_row) 
				# worksheet.write(row_count, 6, line.product_id.categ_id.name  or '', style_table_row) 
				worksheet.write(row_count, 6, line.product_id.default_code  or '', style_table_row) 
				worksheet.write(row_count, 7, line.product_id.name  or '', style_table_row) 
				worksheet.write(row_count, 8, line.product_id.color_type  or '', style_table_row) 
				worksheet.write(row_count, 9, line.product_id.brand.name  or '', style_table_row) 
				worksheet.write(row_count, 10, line.product_id.brand_id.name  or '', style_table_row)
				worksheet.write(row_count, 11, line.product_model  or '', style_table_row)  
				worksheet.write(row_count, 12, line.product_id.carmodel_group1_id.name  or '', style_table_row)
				worksheet.write(row_count, 13, line.product_id.carmodel_group2_id.name  or '', style_table_row)
				worksheet.write(row_count, 14, line.product_id.carmodel_group3_id.name  or '', style_table_row)
				worksheet.write(row_count, 15, line.product_id.cartype_id.name  or '', style_table_row)
				worksheet.write(row_count, 16, line.product_id.fit  or '', style_table_row)
				worksheet.write(row_count, 17, line.product_id.categ_id.parent_id.name  or '', style_table_row)
				worksheet.write(row_count, 18, line.product_id.categ_id.name  or '', style_table_row)
				
				worksheet.write(row_count, 19, line.product_uom_qty  or '', style_table_row) 
				worksheet.write(row_count, 20, line.price_unit  or '', style_table_row) 
				worksheet.write(row_count, 21, line.price_total  or '', style_table_row) 
				# worksheet.write(row_count, 15, line.price_reduce  or '', style_table_row)
				worksheet.write(row_count, 22, line.discount  or '', style_table_row) 
				worksheet.write(row_count, 23, line.price_subtotal  or '', style_table_row)
				if is_admin == True:
					worksheet.write(row_count, 24, line.product_id.foreign_cost  or '', style_table_row) 
					worksheet.write(row_count, 25, line.product_id.exchange_rate  or '', style_table_row) 
					worksheet.write(row_count, 26, line.product_id.local_cost  or '', style_table_row) 
					worksheet.write(row_count, 27, sale.note  or '', style_table_row) 
				else:
					worksheet.write(row_count, 24, sale.note  or '', style_table_row) 
				row_count +=1

		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', 'attachment; filename=%s;'%(filename)
					)])

		workbook.save(response.stream)

		return response
