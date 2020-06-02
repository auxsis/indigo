# -*- coding: utf-8 -*-
{
    'name': "ibas_indigo",

    'summary': """
        IBAS Customizations for Indigo""",

    'description': """
        Long description of module's purpose
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_margin'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
         'security/security_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/product_updater_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}