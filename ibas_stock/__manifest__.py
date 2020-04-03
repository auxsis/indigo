# -*- coding: utf-8 -*-
###################################################################################
#
#    IBAS Pvt. Ltd.
#    Copyright (C) 2019-TODAY IBAS Software Development .
#    Author: Malik Zohaib Rehman
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'Stock Move Analytic and Ageing Analysis',
    'version': '11.0.1.0.2',
    'category': 'Sales',
    'summary': '',
    'author': 'IBAS Software Development',
    'company': 'IBAS Software Development',
    'website': '',
    'depends': ['stock', 'account','stock_account'],
    'demo': [],
    'data': [
        'views/account_report_dropdown.xml',
        'views/stock_picking.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    # 'images': ['static/description/banner.jpg'],
    'qweb': [],
    'license': 'AGPL-3',
}
