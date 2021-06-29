# -*- coding: utf-8 -*-
#/#############################################################################
#
#    DrishtiTech
#    Copyright (C) 2015 (<http://www.drishtitech.com/>).
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
#/#############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import except_orm
from openerp import tools
import datetime

class employee_payin_wizard(osv.osv):
    _name = "employee.pay.in.wiz"

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name' : fields.char('Name'),
        'photo': fields.binary(string='Photo'),
        'employee_id': fields.char('Employee Id'),
        'account_id': fields.char('Account Number'),
        'employee_deposite_id': fields.many2one('employee.deposits', 'Employee Deposite')
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(employee_payin_wizard, self).default_get(cr, uid, fields, context=context)
        emp_deposite_obj = self.pool.get('employee.deposits')
        if context and 'active_id' in context:

            active_id = emp_deposite_obj.search(cr, uid, [('id','=',context.get('active_id'))])
            emp_deposite_id = emp_deposite_obj.browse(cr, uid, active_id)
            if emp_deposite_id:
                res['name'] = emp_deposite_id.name.name
                res['photo'] = emp_deposite_id.name.image_medium
                res['employee_id'] = emp_deposite_id.name.identification_id or " "
                res['account_id'] = emp_deposite_id.name.ean13
                res['employee_deposite_id'] = emp_deposite_id.id
        return res

    def confirm_employee_pay_in(self, cr, uid, ids, context=None):
        uid = 1
        obj = self.browse(cr, uid, ids[0])
        if obj.employee_deposite_id.amount < 1:

            raise osv.except_osv(_('Alert'), _("You can't create invoice with low amount."))
        invoice_lines = [[0, False, {'name': "Pay In", 'price_unit': obj.employee_deposite_id.amount, 'quantity': 1.0}]]
        invoice_obj, invoice_id = self.pool.get('account.invoice'), None
        onchange_partner = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice', obj.employee_deposite_id.name.user_id.partner_id.id)
        default_fields = invoice_obj.fields_get(cr, uid, context)
        invoice_default = invoice_obj.default_get(cr, uid, default_fields, context)
        onchange_partner['value']['partner_id'] = obj.employee_deposite_id.name.user_id.partner_id.id
        onchange_partner['value']['invoice_line'] = invoice_lines
        onchange_partner['value']['employee_deposit_id'] = obj.employee_deposite_id.id
        invoice_default.update(onchange_partner['value'])
        invoice_id = invoice_obj.create(cr, uid, invoice_default)
        invoice_obj.signal_workflow(cr, uid, [invoice_id], 'invoice_open')
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        tree_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        value = {
            'domain': str([('id', '=', invoice_id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(form_view and form_view[1] or False, 'form'),
                      (tree_view and tree_view[1] or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': invoice_id,
            'target': 'current',
            'nodestroy': True
        }

        try:
            template_id = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet', 'email_template_employee_pay_in')
        except ValueError:
            template_id = False
        values = self.pool.get('email.template').generate_email(cr, uid, template_id[1], ids[0], context=context)
        ## Append employee emial id
        if values and 'email_to' in values:
            values['email_to'] = obj.employee_deposite_id.name.work_email
        m_id = self.pool.get('mail.mail').create(cr, uid, values)
        mail_id = self.pool.get('mail.mail').browse(cr,uid, m_id)
        if mail_id:
            mail_send_id = mail_id.send()


        return value
