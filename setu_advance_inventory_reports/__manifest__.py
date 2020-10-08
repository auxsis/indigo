# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Advance Inventory Reports',
    'version' : '11.0',
    'price' : 299,
    'currency'  :'EUR',
    'category': 'stock',
    'summary': """	
        Advance Inventory Reports / Inventory Analysis Reports
        Reports used to analyse inventories by different inventory management techniques.
		""",
    'website' : 'https://www.setuconsulting.com' ,
    'support' : 'support@setuconsulting.com',
    'description' : """
        Advance Inventory Reports / Inventory Analysis Reports
    """,
    'author' : 'Setu Consulting',
    'license' : 'OPL-1',
    'sequence': 25,
    'depends' : ['sale_stock'],
    'images': ['static/description/banner.gif'],
    'data' : [
        'views/setu_stock_movement_report.xml',
        'views/setu_inventory_turnover_analysis_report.xml',
        'views/setu_inventory_fsn_analysis_report.xml',
        'views/setu_inventory_xyz_analysis_report.xml',
        'views/setu_inventory_fsn_xyz_analysis_report.xml',
        'views/setu_inventory_overstock_report.xml',
        'views/setu_inventory_outofstock_report.xml',
        'views/setu_inventory_age_report.xml',
        'views/setu_inventory_age_breakdown_report.xml',
    ],
    'application': True,
    'pre_init_hook': 'pre_init',
    'live_test_url' : 'http://95.111.225.133:8889/web/login',
}
