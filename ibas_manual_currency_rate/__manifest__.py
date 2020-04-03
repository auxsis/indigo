# -*- coding: utf-8 -*-
{
    'name': "Manual Currency Rate",

    'summary': """
        Manual Currency Rate""",

    'description': """Manual Currency Rate""",

    'description': """
        Manual Currency Rate
    """,

    'author': "IBAS",
    'website': "https://ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'wizard/stock_aging_report_view.xml'
        'views/account_invoice_views.xml',
    
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}