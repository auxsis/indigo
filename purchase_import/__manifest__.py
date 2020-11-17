# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Import',
    'category': 'purchase',
    'depends': ['purchase'],
    'data': [
        'views/templates.xml',
        'views/purchase_order_views.xml',
        'wizard/purchase_import_views.xml',
    ],
    'qweb': [
        "static/src/xml/purchase_tree_views.xml",
    ],
    'auto_install': True,
}
