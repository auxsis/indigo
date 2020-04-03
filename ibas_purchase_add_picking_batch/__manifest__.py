# -*- coding: utf-8 -*-
{
    'name': "Add To Purchase From Batch Picking",

    'summary': """
        Add To Purchase From Batch Picking""",

    'description': """Add To Purchase From Batch Picking""",

    'description': """
        Add To Purchase From Batch Picking
    """,

    'author': "IBAS",
    'website': "https://ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase','stock_picking_batch'],

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