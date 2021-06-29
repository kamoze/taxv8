# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'POS Self Service',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'version': '1.0.1',
    'description': """
        POS Self Service
    """,
    'depends': ['base', 'point_of_sale', 'deposite_management'],
    "data": [
        'security/application_security.xml',
       # 'security/ir.model.access.csv',
        'base/wizard/wizard_deposit_view.xml',
        'base/base_view.xml',
        'point_of_sale/point_of_sale_view.xml',
        'views/pos_self_service.xml',
        'wizard/shop_report_wiz_view.xml',
        'wizard/pos_self_service_wiz_view.xml',
        'report/template_shop_report.xml',
        'report/report.xml',
        'report/expanded_orders_report_view.xml',
        'wizard/pos_order_confirm_wiz_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/backend.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
