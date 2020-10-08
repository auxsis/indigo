# -*- coding: utf-8 -*-
{
    'name': "IBAS_Indigo Product",

    'summary': """
        IBAS Customizations for Product""",

    'description': """
        This module contains customizations for products
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
         # Data
         'data/res_groups_data.xml',

         # Security
         'security/ir.model.access.csv',

         # Views
        'views/product_template_ext_views.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}