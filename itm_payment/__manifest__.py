# -*- coding: utf-8 -*-
# Odoo, Open Source Itm Payment.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

{
    'name': 'Account Payment Voucher',
    'category': 'Account',
    'author': 'Odoowikia',
    'website': 'http://odoowikia.com/',
    'description': """
================================================================================

1. Account Payment Management.

================================================================================
""",
    'depends': ['base', 'web', 'account', 'payment' ],
    'summary': 'Manage internal transfer For Payment.',
    'data': [
        'views/account_payment_view.xml',
        'views/payment_voucher_view.xml'],
    'price': '25.00',
    'currency': "EUR",
     'images':['static/description/Banner.png'],
    'installable': True,
}
