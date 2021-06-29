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

from openerp import fields, models, api,_
from datetime import date,datetime


class shop_report_wizard(models.TransientModel):
    _name = 'shop.report.wizard'
    _description = 'Shop Report'


    date_start = fields.Date('Date Start', default=date.today(), required=True)
    date_end = fields.Date('Date End', default=date.today(), required=True)
    state = fields.Selection([('draft', 'New'), ('paid', 'Paid'), ('done', 'Done')], 'State', required=True)
    payment_method_ids = fields.Many2many('account.journal', 'pos_shop_payment_rel1', 'wizard_id', 'journal_id','Journal')
    interface = fields.Selection([('self_service', 'Self Service'), ('normal', 'Normal')], default='self_service', string='POS Interface')
    location_ids = fields.Many2many('stock.location','pos_location_rel1', 'wizard_id', 'location_id', 'Location')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.ids,
            'model': 'shop.report.wizard',
            'form': data
        }
        return self.env['report'].get_action(self, 'employee_pos_ewallet.template_shop_report', data=datas)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
