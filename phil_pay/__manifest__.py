# -*- coding: utf-8 -*-
{
    'name': "phil_pay",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr', 'hr_attendance', 'hr_payroll', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/payroll_contribution_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_raw_attendance.xml',
        'views/hr_employee_loands.xml',
        'views/payroll_contribution_table_views.xml',
        'data/salary_rules.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}