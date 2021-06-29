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
from openerp import SUPERUSER_ID

class emp_pay_out(osv.osv):
    _name = 'emp.pay.out'
    _rec_name = 'account_id'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def onchange_account_id(self, cr, uid, ids, account_id, context=None):
        uid = SUPERUSER_ID
        res = {'value': {}}
        emp_pool = self.pool.get('hr.employee')
        if account_id:
            emp_id = emp_pool.search(cr, uid, [('ean13', '=', account_id)])
            if not emp_id:
                emp_id = emp_pool.search(cr, uid, [('identification_id', '=', account_id)])
                if not emp_id:
                    raise except_orm(_('Warning!'),
                                 _("Beneficiary not found, Please input correct Number."))

            employee_id = emp_pool.browse(cr, uid, emp_id)
            if employee_id:
                res['value'] = {'current_balance': employee_id.available_balance}
        return res


    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        uid = SUPERUSER_ID
        res = {'value': {}}
        emp_pool = self.pool.get('hr.employee')
        if employee_id:
            emp_id = emp_pool.search(cr, uid, [('id', '=', employee_id)])

            employee_id = emp_pool.browse(cr, uid, emp_id)
            if employee_id:
                res['value'] = {'current_balance': employee_id.available_balance}
        return res


    _columns = {
        'account_id': fields.char("Account Id"),
        'employee_id': fields.many2one('hr.employee', 'Employee Name'),
        'pay_out_date': fields.datetime("Date"),
        'user': fields.char("User"),
        'current_balance':fields.float(string='Current Balance'),
    }

    def create(self, cr, uid, vals, context=None):
        uid = SUPERUSER_ID
        emp_pool = self.pool.get('hr.employee')
        if vals and 'account_id' in vals and vals.get('account_id'):
            emp_id = emp_pool.search(cr, uid, [('ean13', '=', vals.get('account_id'))])
            if not emp_id:
                emp_id = emp_pool.search(cr, uid, [('identification_id', '=', vals.get('account_id'))])
                if not emp_id:
                    raise except_orm(_('Warning!'),
                                 _("Beneficiary not found, Please input correct Number."))
        elif vals and 'employee_id' in vals:
            emp_id = vals.get('employee_id')
        if emp_id:
            employee_id = emp_pool.browse(cr, uid, emp_id)
            if employee_id:
                vals.update({'current_balance': employee_id.available_balance})
        return super(emp_pay_out, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        uid = SUPERUSER_ID
        emp_pool = self.pool.get('hr.employee')
        if vals and 'account_id' in vals  and  vals.get('account_id'):
            emp_id = emp_pool.search(cr, uid, [('ean13', '=', vals.get('account_id'))])
            if not emp_id:
                emp_id = emp_pool.search(cr, uid, [('identification_id', '=', vals.get('account_id'))])
                if not emp_id:
                    raise except_orm(_('Warning!'),
                                 _("Beneficiary not found, Please input correct Number."))
        elif vals and 'employee_id' in vals:
            emp_id = vals.get('employee_id')
        if emp_id:
            employee_id = emp_pool.browse(cr, uid, emp_id)
            if employee_id:
                vals.update({'current_balance': employee_id.available_balance})
        res = super(emp_pay_out, self).write(cr, uid, ids, vals, context=context)
        return res

    def _get_user_name(self, cr, uid, *args):
        user_obj = self.pool.get('res.users')
        user_value = user_obj.browse(cr, uid, uid)
        return user_value.login or False

    _defaults = {
        'pay_out_date': lambda *a: datetime.datetime.now(),
        # 'user': _get_user_name,
    }

    def emp_button_pay_money(self, cr, uid, ids, context=None):
        """ function will call on pay out form open wizard for pay money """
        uid = SUPERUSER_ID
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet', 'employee_pay_money_wiz')
        return {
            'name': _('Money Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.money.payment',
            'view_id': form_view[1],
            'target': 'new',
        }

class employee_money_payment(osv.osv_memory):
    _name ="employee.money.payment"


    _columns = {
        'account_id': fields.char('Account Id'),
        'name': fields.char('Name'),
        'photo': fields.binary(string='Photo'),
        'date':fields.datetime("Date"),
        'employee_id': fields.char('Employee Id'),
        'current_balance':fields.float(string='Current Balance'),
        'amount_to_pay': fields.float('Amount'),
        'pay_out_id': fields.many2one('emp.pay.out', 'Pay Out Id'),
        'emp_id': fields.many2one('hr.employee', 'Employee'),
    }

    _defaults = {
        'date': lambda *a: datetime.datetime.now(),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(employee_money_payment, self).default_get(cr, uid, fields, context=context)
        uid = SUPERUSER_ID
        # res.update(self.get_oauth_providers(cr, uid, fields, context=context))
        pay_out_obj = self.pool.get('emp.pay.out')
        emp_pool = self.pool.get('hr.employee')
        if context and 'active_id' in context:
            # active_id = context.get('active_id')

            active_id = pay_out_obj.search(cr, uid, [('id','=',context.get('active_id'))])
            pay_out_id = pay_out_obj.browse(cr, uid, active_id)
            if pay_out_id:
                if pay_out_id.account_id:
                    emp_id = emp_pool.search(cr, uid, [('ean13','=',pay_out_id.account_id)])
                    if not emp_id:
                        emp_id = emp_pool.search(cr, uid, [('identification_id', '=', pay_out_id.account_id)])
                else:
                    emp_id = pay_out_id.employee_id.id
                if emp_id:
                    employee_id = emp_pool.browse(cr, uid, emp_id)
                    res['name'] = employee_id.name
                    res['photo'] = employee_id.image_medium,
                    res['employee_id'] = employee_id.identification_id or " "
                    res['account_id'] = employee_id.ean13 or employee_id.ean13
                    res['pay_out_id'] = pay_out_id.id
                    res['emp_id'] = employee_id.id
        # self.onchange_account_id(self, cr, uid, [active_id], pay_out_id.account_id)
        return res

    def confirm_emp_pay_out(self, cr, uid, ids, context=None):
        """ To confirm pay out and create expense lines """
        uid = 1
        obj = self.browse(cr, uid, ids[0])
        if obj.emp_id.available_balance < obj.amount_to_pay:
            raise osv.except_osv(_('Alert'), _("Insufficient Fund."))

        if obj.amount_to_pay < 1:
            raise osv.except_osv(_('Alert'), _("You can't create Expense with low amount."))
        #
        if obj.amount_to_pay:
            expense_vals = {
                'name': obj.emp_id.id,
                'amount': obj.amount_to_pay,
                'date': datetime.datetime.now(),
                'source': "Pay Out",
                'create_invoice': False,
            }

            self.pool.get('employee.expenses').create(cr, uid, expense_vals, context = context)





        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet', 'employee_pay_money_confirmation_msg_wiz')

        try:
            template_id = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet', 'email_template_employee_pay_out')
        except ValueError:
            template_id = False
        values = self.pool.get('email.template').generate_email(cr, uid, template_id[1], ids[0], context=context)
        ## Append employee emial id
        if values and 'email_to' in values:
            values['email_to'] = obj.emp_id.work_email

        m_id = self.pool.get('mail.mail').create(cr, uid, values)
        mail_id = self.pool.get('mail.mail').browse(cr,uid, m_id)
        if mail_id:
            mail_send_id = mail_id.send()


        return {
            'name': _('Money Confirmation Message'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.money.payment',
            'view_id': form_view[1],
            'target': 'new',
        }

# class payment_confirmation_msg(osv.osv_memory):
#     _name = "confirm.payment.msg"
#     ## Confirmaion message
