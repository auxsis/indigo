# -*- coding: utf-8 -*-
from odoo import http

# class IbasIndigo(http.Controller):
#     @http.route('/ibas_indigo/ibas_indigo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_indigo/ibas_indigo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_indigo.listing', {
#             'root': '/ibas_indigo/ibas_indigo',
#             'objects': http.request.env['ibas_indigo.ibas_indigo'].search([]),
#         })

#     @http.route('/ibas_indigo/ibas_indigo/objects/<model("ibas_indigo.ibas_indigo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_indigo.object', {
#             'object': obj
#         })