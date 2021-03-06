# -*- coding: utf-8 -*-
{
    'name': "indigo_prod",

    'summary': """
        Indigo - IBAS Customizations""",

    'description': """
        - Product Fields
        - Sales Security and Access Right
        - Reporting
            - Sales Report Export Wizard and Report
        - VEndor Bill: Manual Currency Rate Update
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'r2d2', 'product', 'stock', 'stock_picking_batch', 'delivery', 'hr_disciplinary_tracking', 'bi_account_cheque', 'hr_expense', 'account', 'account_reports', 'account_reports_followup', 'purchase', 'ibas_indigo', 'bank_reconciliation', 'dev_customer_account_statement', 'bi_customer_overdue_statement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/indigo_security.xml',
        # 'data/menu_data.xml',
        'data/report_paperformat_data.xml',
        'data/report_data.xml',
        'views/assets.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/indigo_products.xml',
        'views/indigo_partners.xml',
        'views/layout_templates.xml',
        'views/account_payment_views.xml',
        'views/account_invoice_views.xml',
        'views/sales_order_views.xml',
        'views/delivery_views.xml',
        'views/stock_picking_views.xml',
        'views/account_bank_statement_views.xml',
        'views/hr_views.xml',
        'views/hr_expense_views.xml',
        'views/account_cheque_views.xml',
        'views/stock_picking_batch_views.xml',
        'views/stock_move_views.xml',
        'views/report_followup.xml',
        'views/account_check_batch.xml',
        'views/account_customer_statement.xml',
        'views/account_move_views.xml',
        'views/res_users_views.xml',
        'report/report_saleorder.xml',
        'report/report_cheque_deposit_slip.xml',
        'report/report_cheque_print.xml',
        'report/report_customer_statement.xml',
        'wizard/sales_report_export_view.xml',
        'wizard/sales_report_export_by_invoice_view.xml',
        'wizard/stock_pick_item_report_view.xml',
        'wizard/sales_report_outstock_item_view.xml',
        'wizard/stock_picking_return_views.xml',
        'wizard/customer_statement_views.xml',
        'wizard/sales_delete_posted_view.xml',
        'views/menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
