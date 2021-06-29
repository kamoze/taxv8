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

from openerp import fields, models, api, _
from datetime import date, datetime
from openerp.exceptions import ValidationError
from lxml import etree
from openerp.osv.orm import setup_modifiers

class pos_self_service_wizard(models.TransientModel):
    _name = 'pos.self.service.wizard'
    _description = 'POS Self Service'


    def _get_current_emp(self):
        user = self.env.user
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)])[0]
        if employee:
            return employee
        return



    user_type = fields.Selection([('staff', 'Staff')], string="User Type", required=True, default='staff', readonly=True)

    staff_id = fields.Many2one('hr.employee', string="Staff Name", default=_get_current_emp, readonly="1")
    PIN = fields.Char(string="PIN")
    stock_location_id = fields.Many2one('stock.location', string="Shop", domain=[('usage', '=', 'internal')], required=True)

    @api.constrains('PIN')
    def check_pin(self):
        # if self.user_type == 'student':
        #     if self.PIN != self.student_id.pin:
        #         raise ValidationError(_('Entered PIN is wrong..'))
        #     if self.student_id.stud_balance_amount <= 0:
        #         raise ValidationError(_('Insufficient Balance. Please credit your account.'))

        if self.user_type == 'staff':
            if self.PIN != self.staff_id.pin:
                raise ValidationError(_('Entered PIN is wrong..'))
            if self.staff_id.available_balance <= 0:
                raise ValidationError(_('Insufficient Balance. Please credit your account.'))

    @api.multi
    def pos_self_service_login(self):
        view_id = self.env['ir.model.data'].get_object_reference('employee_pos_ewallet', 'aspl_view_pos_pos_form')[1]
        pos_obj =   self.env['pos.session'].sudo().search([('state', '=', 'opened')])
        product_list = []
        ## get all product list and append to pos order lines

        product_ids = self.env['product.product'].sudo().search([('qty_available', '>', 0.0)])


        for product_id in product_ids:
            available_qty = product_id.sudo().with_context({'location' : self.stock_location_id.id}).qty_available
            if available_qty > 0:
                line_vals = {
                    'image': product_id.image_medium,
                    'product_id': product_id.id,
                    'price_unit':product_id.lst_price,
                    'pro_current_available_qty':available_qty or 0,
                    'qty': 0.0,
                }
                product_list.append([0, 0, line_vals])

        return {
            'type': 'ir.actions.act_window',
            'name': _('POS Order'),
            'res_model': 'pos.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'context' :{

                'default_employee_id': self.staff_id.id or False,
                'default_stock_location_id':self.stock_location_id.id,
                'default_lines': product_list,
                'default_session_id': pos_obj.id
            },
            'target': 'new',
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(pos_self_service_wizard, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            erp_group_id = self.env['ir.model.data'].get_object_reference('base', 'group_erp_manager')[1]
            user_group_ids = self.env['res.users'].browse(self._uid).groups_id.ids
            if erp_group_id in user_group_ids:
                for node in doc.xpath("//field[@name='user_type']"):
                    node.set('readonly', '0')
                    setup_modifiers(node, res['fields']['user_type'])
                for node in doc.xpath("//field[@name='student_id']"):
                    node.set('readonly', '0')
                    setup_modifiers(node, res['fields']['student_id'])
                for node in doc.xpath("//field[@name='staff_id']"):
                    node.set('readonly', '0')
                    setup_modifiers(node, res['fields']['staff_id'])
        res['arch'] = etree.tostring(doc)
        return res

class pos_order_confirm_wizard(models.TransientModel):
    _name = 'pos.order.confirm.wizard'

    order_id = fields.Many2one('pos.order', string="Order")

    @api.multi
    def order_confirm(self):
        if self.order_id:
            for line in self.order_id.lines:
                if line.qty == 0:
                    line.unlink()
            self.order_id.sudo().copy_check()

    @api.multi
    def order_delete(self):
        if self.order_id:
            self.order_id.session_id.write({'sequence_number' : self.order_id.session_id.sequence_number - 1})
            self.order_id.unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
