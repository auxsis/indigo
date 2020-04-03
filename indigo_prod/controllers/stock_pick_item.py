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


class ExportStockPickItemReport(http.Controller):

	@http.route('/web/export_xls/stock_pick_item_report', type='http', auth="user")
	def export_xls(self, filename, date_from, date_to, user_id, **kw):
		user_id = ast.literal_eval(user_id)

		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Stock Pick Item Report')

		stock_picking_ids = request.env['stock.picking'].sudo().search([('scheduled_date','>=',date_from),('scheduled_date','<=',date_to),('state','=','assigned'),('picking_type_id','in',[2])],order='scheduled_date desc')
		
		# STYLES
		style_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: wrap no")
		style_header_right = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no")
		style_table_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz centre, vert centre, wrap on;borders: top thin, bottom thin, right thin;")
		style_table_row = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom thin, right thin;")
		style_table_row_amount = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom thin, right thin;", num_format_str="#,##0.00")
		style_table_total = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom medium, right thin;")
		style_table_total_value = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom medium, right thin;", num_format_str="#,##0.00")
		style_end_report = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz left, wrap no;")
		worksheet.col(0).width = 500*12
		worksheet.col(1).width = 500*12
		worksheet.col(2).width = 500*12
		worksheet.col(3).width = 500*12
		worksheet.col(4).width = 300*12
		worksheet.col(5).width = 300*12
		worksheet.col(6).width = 500*12
		worksheet.col(7).width = 300*12
		worksheet.col(8).width = 300*12
		worksheet.col(9).width = 300*12
		worksheet.col(10).width = 300*12
		worksheet.col(11).width = 250*12


		# TEMPLATE HEADERS

		# TABLE HEADER
		worksheet.write(0, 0, 'Floor Location', style_table_header_bold) # HEADER
		worksheet.write(0, 1, "Rack Location", style_table_header_bold) # HEADER
		worksheet.write(0, 2, 'Agent', style_table_header_bold) # HEADER
		worksheet.write(0, 3, 'Customer', style_table_header_bold) # HEADER
		worksheet.write(0, 4, 'SO No.', style_table_header_bold) # HEADER
		worksheet.write(0, 5, 'Item Code', style_table_header_bold) # HEADER
		worksheet.write(0, 6, 'Item Description', style_table_header_bold) # HEADER
		worksheet.write(0, 7, 'Color/Type', style_table_header_bold) # HEADER
		worksheet.write(0, 8, 'Brand Model', style_table_header_bold) # HEADER
		worksheet.write(0, 9, 'Car Model', style_table_header_bold) # HEADER
		worksheet.write(0, 10, 'Car Brand', style_table_header_bold) # HEADER
		worksheet.write(0, 11, 'Qty', style_table_header_bold) # HEADER

		row_count = 1

		for pick in stock_picking_ids:
			sale = request.env['sale.order'].sudo().search([('id','=',pick.sale_id.id)])
			sale_number = sale.name
			sale_customer = sale.partner_id.name
			sale_user = sale.user_id.name

			if not user_id or user_id == sale.user_id.id:

				for line in pick.move_lines:
					worksheet.write(row_count, 0, line.product_id.floor_location or '', style_table_row) 
					worksheet.write(row_count, 1, line.product_id.rack_location  or '', style_table_row) 
					worksheet.write(row_count, 2, sale_user  or '', style_table_row) 
					worksheet.write(row_count, 3, sale_customer  or '', style_table_row) 
					worksheet.write(row_count, 4, sale_number or '', style_table_row) 
					worksheet.write(row_count, 5, line.product_id.default_code or '', style_table_row) 
					worksheet.write(row_count, 6, line.product_id.name  or '', style_table_row) 
					worksheet.write(row_count, 7, line.product_id.color_type  or '', style_table_row) 
					worksheet.write(row_count, 8, line.product_id.brand.name  or '', style_table_row) 
					worksheet.write(row_count, 9, line.product_id.carmodel_id.name  or '', style_table_row) 
					worksheet.write(row_count, 10, line.product_id.brand_id.name  or '', style_table_row)
					worksheet.write(row_count, 11, line.product_uom_qty  or '', style_table_row)  
					
					row_count +=1

		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', 'attachment; filename=%s;'%(filename)
					)])

		workbook.save(response.stream)

		return response
