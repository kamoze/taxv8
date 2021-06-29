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



class student_payout(osv.osv):
    _name ='student.pay.out'
    _rec_name = 'account_id'


    def onchange_account_id(self, cr, uid, ids, account_id, context=None):
        uid = SUPERUSER_ID
        res = {'value': {}}
        student_pool = self.pool.get('op.student')
        if account_id:
            stud_id = student_pool.search(cr, uid, [('ean13', '=', account_id)])
            if not stud_id:
                stud_id = student_pool.search(cr, uid, [('gr_no', '=', account_id)])
                if not stud_id:
                    raise except_orm(_('Warning!'),
                                 _("Beneficiary not found, Please input correct Number."))
            student_id = student_pool.browse(cr, uid, stud_id)
            if student_id:
                res['value'] = {'current_balance': student_id.stud_balance_amount}
        return res

    def onchange_student_id(self, cr, uid, ids, student_id, context=None):
        uid = SUPERUSER_ID
        res = {'value': {}}
        student_pool = self.pool.get('op.student')
        if student_id:
            stud_id = student_pool.search(cr, uid, [('id', '=', student_id)])
            student_id = student_pool.browse(cr, uid, stud_id)
            if student_id:
                res['value'] = {'current_balance': student_id.stud_balance_amount}
        return res

    def create(self, cr, uid, vals, context=None):
        uid = SUPERUSER_ID
        student_pool = self.pool.get('op.student')
        if vals and 'account_id' in vals and vals.get('account_id'):
            stud_id = student_pool.search(cr, uid, [('ean13', '=', vals.get('account_id'))])
            if not stud_id:
                stud_id = student_pool.search(cr, uid, [('gr_no', '=', vals.get('account_id'))])
                if not stud_id:
                    raise except_orm(_('Warning!'),
                                     _("Beneficiary not found, Please input correct Number."))
        elif vals and 'student_id' in vals:
            stud_id = vals.get('student_id')
        if stud_id:
            student_id = student_pool.browse(cr, uid, stud_id)
            if student_id:
                vals.update({'current_balance': student_id.stud_balance_amount})
        return super(student_payout, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        uid = SUPERUSER_ID
        student_pool = self.pool.get('op.student')
        if vals and 'account_id' in vals and vals.get('account_id'):
            stud_id = student_pool.search(cr, uid, [('ean13', '=', vals.get('account_id'))])
            if not stud_id:
                stud_id = student_pool.search(cr, uid, [('gr_no', '=', vals.get('account_id'))])
                if not stud_id:
                    raise except_orm(_('Warning!'),
                                     _("Beneficiary not found, Please input correct Number."))
        elif vals and 'student_id' in vals:
            stud_id = vals.get('student_id')
        if stud_id:
            student_id = student_pool.browse(cr, uid, stud_id)
            if student_id:
                vals.update({'current_balance': student_id.stud_balance_amount})
        res = super(student_payout, self).write(cr, uid, ids, vals, context=context)
        return res

    _columns = {
        'account_id': fields.char("Account Id"),
        'student_id': fields.many2one('op.student', 'Student Name'),
        'pay_out_date': fields.datetime("Date"),
        'user': fields.char("User"),
        'current_balance':fields.float('Current Balance')
    }

    def _get_user_name(self, cr, uid, *args):
        user_obj = self.pool.get('res.users')
        user_value = user_obj.browse(cr, uid, uid)
        return user_value.login or False

    _defaults = {
        'pay_out_date': lambda *a:datetime.datetime.now(),
        # 'user': _get_user_name,
    }

    def button_pay_money(self, cr, uid, ids, context=None):
        """ function will call on pay out form open wizard for pay money """
        uid = SUPERUSER_ID
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'deposite_management', 'student_pay_money_wiz')
        return {
            'name': _('Money Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'student.money.payment',
            'view_id': form_view[1],
            'target': 'new',
        }


class student_money_payment(osv.osv_memory):
    _name ="student.money.payment"

    _columns = {
        'account_id': fields.char('Account Id'),
        'name': fields.char('Name'),
        'photo': fields.binary(string='Photo'),
        'date': fields.datetime("Date"),
        'matric_number': fields.char('Matric Number'),
        'session_id': fields.many2one('op.sessions', 'Session'),
        'semester_id': fields.many2one('op.batch', 'Semester'),
        'current_balance':fields.float('Current Balance'),
        'amount_to_pay': fields.float('Amount'),
        'pay_out_id': fields.many2one('student.pay.out', 'Pay Out Id'),
        'student_id': fields.many2one('op.student', 'Student'),
    }

    _defaults = {
        'date': lambda *a: datetime.datetime.now(),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(student_money_payment, self).default_get(cr, uid, fields, context=context)
        uid = SUPERUSER_ID
        # res.update(self.get_oauth_providers(cr, uid, fields, context=context))
        pay_out_obj = self.pool.get('student.pay.out')
        student_pool = self.pool.get('op.student')
        if context and 'active_id' in context:
            # active_id = context.get('active_id')

            active_id = pay_out_obj.search(cr, uid, [('id','=',context.get('active_id'))])
            pay_out_id = pay_out_obj.browse(cr, uid, active_id)
            if pay_out_id:
                if pay_out_id.account_id:
                    stud_id = student_pool.search(cr, uid, [('ean13','=',pay_out_id.account_id)])
                    if not stud_id:
                        stud_id = student_pool.search(cr, uid, [('gr_no', '=', pay_out_id.account_id)])
                else:
                    stud_id = pay_out_id.student_id.id
                if stud_id:
                    student_id = student_pool.browse(cr, uid, stud_id)
                    res['name'] = student_id.last_name + '' + student_id.middle_name + ''+ student_id.name
                    res['photo'] = student_id.photo
                    res['matric_number'] = student_id.gr_no or " "
                    res['account_id'] = student_id.ean13 or pay_out_id.student_id.ean13
                    res['session_id'] = student_id.session_id.id
                    res['semester_id'] = student_id.batch_id.id
                    # res['current_balance'] = student_id.stud_balance_amount or 0.00,
                    res['pay_out_id'] = pay_out_id.id
                    res['student_id'] = student_id.id
        return res

    def confirm_pay_out(self, cr, uid, ids, context=None):
        """ To confirm pay out and create expense lines """
        uid = 1
        uid = SUPERUSER_ID
        obj = self.browse(cr, uid, ids[0])
        if  obj.student_id.stud_balance_amount < obj.amount_to_pay:
            raise osv.except_osv(_('Alert'), _("Insufficient Fund."))

        if obj.amount_to_pay < 1:
            raise osv.except_osv(_('Alert'), _("You can't create Expense with low amount."))

        if obj.amount_to_pay:
            expense_vals = {
                'name': obj.student_id.id,
                'amount': obj.amount_to_pay,
                'date': datetime.datetime.now(),
                'source': "Pay Out",
                'create_invoice': False,
            }

            student_expenses_id = self.pool.get('student.expenses').create(cr, uid, expense_vals, context = context)

        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'deposite_management',
                                                     'student_pay_money_confirmation_msg_wiz')

        try:
            template_id = models_data.get_object_reference(cr, uid, 'deposite_management', 'email_template_student_pay_out')
            values = self.pool.get('email.template').generate_email(cr, uid, template_id[1], ids[0], context=context)
            ## Append employee emial id
            if values and 'email_to' in values:
                values['email_to'] = obj.student_id.email
            m_id = self.pool.get('mail.mail').create(cr, uid, values)
            mail_id = self.pool.get('mail.mail').browse(cr, uid, m_id)
            if mail_id:
                mail_send_id = mail_id.send()
        except ValueError:
            template_id = False


        return {
            'name': _('Money Confirmation Message'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'student.money.payment',
            'view_id': form_view[1],
            'target': 'new',
        }