# -*- coding: utf-8 -*-
{
    'name': "IBAS Stockout",

    'summary': """
        Stockout Order""",

    'description': """Stockout Order""",

    'description': """
        Stockout Order
    """,

    'author': "IBAS",
    'website': "https://ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sales_team','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/stockout_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}