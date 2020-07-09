{
    'name': 'Picking Batch Vendor Bill',
    'summary': "Create vendor bill from batch picking.",
    'version': '11.0.0.1.0',
    'category': 'stock',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://jupical.com/',
    'depends': ['stock_picking_batch', 'account', 'account_accountant', 'purchase'],
    'license': 'AGPL-3',
    'data': [
        'views/res_config_settings_view.xml',
        'views/stock_picking_batch_view.xml', ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
