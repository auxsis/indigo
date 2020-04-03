# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Petty Cash.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Petty Cash Management',
    'category': 'Account',
    'author': 'Odoowikia',
    'website': 'http://odoowikia.com/',
    'description': """
================================================================================

1. Petty Cash Management .

================================================================================
""",
    'depends': [ 'itm_payment_analytic', 'hr', 'base', 'web', 'analytic', 'account'],
     'summary': 'Manage Petty Cash Funds',
    'data': [
        'security/ir.model.access.csv',
        'security/petty_cash_access.xml',
        'data/memo_sequence.xml',
        'report/petty_cash_report_template.xml',
        'views/assets.xml',
         'views/petty_cash_dashboard.xml',
        'views/petty_cash_view.xml',
        'views/employee_view.xml',
         'custom_report.xml',
        ],
        'qweb': [
        "static/src/xml/attachmnet_widget.xml",
        "static/src/xml/extra_preview_content.xml",
        "static/src/xml/preview_content.xml",
        "static/src/xml/video_preview_content.xml",
        "static/src/xml/doc_preview_content.xml",
        "static/src/xml/petty_cash_dashboard.xml",
        "static/src/xml/preview_dialog.xml",
    ],
     'images':['static/description/Banner.png'],
    'price': '49.00',
    'currency': "EUR",
    'installable': True,

}
