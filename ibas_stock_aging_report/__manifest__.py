# -*- coding: utf-8 -*-
{
    'name': "Stock Aging Report",

    'summary': """
        Stock Aging Report""",

    'description': """Stock Aging Report""",

    'description': """
        Stock Aging Report
    """,

    'author': "IBAS",
    'website': "https://ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/layout_templates.xml',
        'report/stock_aging_views.xml',
        'views/report.xml',
        'wizard/stock_aging_report_view.xml'
    
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}