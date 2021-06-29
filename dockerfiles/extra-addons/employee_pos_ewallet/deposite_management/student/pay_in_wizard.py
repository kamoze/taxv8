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
import math

class student_payin_wizard(osv.osv):
    _name = "student.pay.in.wiz"

    _columns = {
        'name' : fields.char('Name'),
        'photo': fields.binary(string='Photo'),
        'matric_number': fields.char('Matric Number'),
        'account_id': fields.char('Account Number'),
        'session_id': fields.many2one('op.sessions', 'Session'),
        'semester_id': fields.many2one('op.batch', 'Semester'),
        'student_deposite_id': fields.many2one('student.deposits', 'Student Deposite')
    }



    def default_get(self, cr, uid, fields, context=None):
        res = super(student_payin_wizard, self).default_get(cr, uid, fields, context=context)
        # res.update(self.get_oauth_providers(cr, uid, fields, context=context))
        student_deposite_obj = self.pool.get('student.deposits')
        if context and 'active_id' in context:
            # active_id = context.get('active_id')

            active_id = student_deposite_obj.search(cr, uid, [('id','=',context.get('active_id'))])
            student_deposite_id = student_deposite_obj.browse(cr, uid, active_id)
            if student_deposite_id:
                res['name'] = student_deposite_id.name.last_name + '' + student_deposite_id.name.middle_name + ''+ student_deposite_id.name.name
                res['photo'] = student_deposite_id.name.photo
                res['matric_number'] = student_deposite_id.name.gr_no
                res['account_id'] = student_deposite_id.name.ean13
                res['session_id'] = student_deposite_id.name.session_id.id
                res['semester_id'] = student_deposite_id.name.batch_id.id
                res['student_deposite_id'] = student_deposite_id.id
        return res

    def confirm_student_pay_in(self, cr, uid, ids, context=None):
        uid = 1
        obj = self.browse(cr, uid, ids[0])
        if obj.student_deposite_id.amount < 1:
            raise osv.except_osv(_('Alert'), _("You can't create invoice with low amount."))
        invoice_lines = [[0, False, {'name': "Pay In", 'price_unit': obj.student_deposite_id.amount, 'quantity': 1.0}]]
        invoice_obj, invoice_id = self.pool.get('account.invoice'), None
        voucher_obj = self.pool.get('account.voucher')
        onchange_partner = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice',
                                                           obj.student_deposite_id.name.user_id.partner_id.id)
        default_fields = invoice_obj.fields_get(cr, uid, context)
        invoice_default = invoice_obj.default_get(cr, uid, default_fields, context)
        onchange_partner['value']['partner_id'] = obj.student_deposite_id.name.user_id.partner_id.id
        onchange_partner['value']['student_id'] = obj.student_deposite_id.name.id
        onchange_partner['value']['invoice_line'] = invoice_lines
        onchange_partner['value']['stud_deposit_id'] = obj.student_deposite_id.id
        ## add student info on change of partner (Student)
        onchange_partner['value']['stud_matric_number'] = obj.student_deposite_id.name.gr_no
        onchange_partner['value']['couese_id'] = obj.student_deposite_id.name.course_id.id
        onchange_partner['value']['entry_session_id'] = obj.student_deposite_id.name.session_id.id
        onchange_partner['value']['semester_id'] = obj.student_deposite_id.name.batch_id.id

        invoice_default.update(onchange_partner['value'])
        invoice_id = invoice_obj.create(cr, uid, invoice_default)
        invoice_obj.signal_workflow(cr, uid, [invoice_id], 'invoice_open')
        invoice_obj.signal_workflow(cr, uid, [invoice_id], 'paid')
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

        self.write(cr, uid, ids, {'create_invoice': True})
        return value



        ## Voucher creaion logic
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type','=','cash'),('sequence_id.name','=','cash')])
        journal_id = self.pool.get('account.journal').browse(cr, uid, journal_id)
        inv_id = invoice_obj.browse(cr, uid, invoice_id)
        voucher_dic = {
            'name': inv_id.name,
            'reference': inv_id.reference,
            'journal_id': journal_id.id,
            'company_id': inv_id.company_id.id,
            'partner_id': inv_id.partner_id.id,
            'amount': obj.student_deposite_id.amount,
            'date': inv_id.date_invoice or False,
            'account_id': journal_id.default_credit_account_id.id or journal_id.default_debit_account_id.id,
            'type': inv_id.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
        }
        partner_ochg = voucher_obj.onchange_partner_id(cr, uid, [], inv_id.partner_id.id, journal_id.id, obj.student_deposite_id.amount,
                                                       inv_id.company_id.currency_id.id, 'payment',
                                                       inv_id.date_invoice, context)
        if partner_ochg.get('value', False):
            voucher_dic.update(partner_ochg.get('value'))
        date_ochg = voucher_obj.onchange_date(cr, uid, [], inv_id.date_invoice, inv_id.company_id.currency_id.id,
                                               False, obj.student_deposite_id.amount, inv_id.company_id.id, context)

        if date_ochg.get('value', False):
            voucher_dic.update(date_ochg.get('value'))
        voucher_ochg = voucher_obj.onchange_amount(cr, uid, [], obj.student_deposite_id.amount, 1.0, inv_id.partner_id.id,
                                                   journal_id.id, inv_id.company_id.currency_id.id, 'payment',
                                                   inv_id.date_invoice, False, inv_id.company_id.id, context)
        if voucher_ochg.get('value', False):
            voucher_dic.update(voucher_ochg.get('value'))
        journal_ochg = voucher_obj.onchange_journal(cr, uid, [],journal_id.id, [], False, inv_id.partner_id.id,
                                                    inv_id.date_invoice, obj.student_deposite_id.amount, 'payment',
                                                    inv_id.company_id.id, context)
        # if journal_ochg.get('value', False):
        #     voucher_dic.update(journal_ochg.get('value'))
        #
        # if voucher_dic.get('line_cr_ids', False):
        #     line_cr_ids = []
        #     for line in voucher_dic.get('line_cr_ids'):
        #         line_cr_ids.append((0, 0, line))
        #     voucher_dic['line_cr_ids'] = line_cr_ids
        # if voucher_dic.get('line_dr_ids', False):
        # #     sequence item 0: expected string, NoneType found
        #     line_dr_ids = []
        #     for line in voucher_dic.get('line_dr_ids'):
        #         line_dr_ids.append((0, 0, line))
        #     voucher_dic['line_dr_ids'] = line_dr_ids
        # voucher_id = voucher_obj.create(cr, uid, voucher_dic, context)
        # voucher_obj.button_proforma_voucher(cr, uid, [voucher_id], context={})
        # kdkjkkkkkk

        # {'value': {'line_cr_ids': [], 'account_id': 8, 'paid_amount_in_company_currency': 100.0, 'line_dr_ids': [],
        #            'currency_help_label': u'At the operation date, the exchange rate was\n1.00 \u20a6 = 1.00 \u20a6',
        #            'currency_id': 125, 'pre_line': False, 'payment_rate': 1.0,
        #            'payment_rate_currency_id': 125}} - ---------partner_ochg


        try:
            template_id = models_data.get_object_reference(cr, uid, 'deposite_management', 'email_template_student_pay_in')
        except ValueError:
            template_id = False
        values = self.pool.get('email.template').generate_email(cr, uid, template_id[1], ids[0], context=context)
        ## Append employee emial id
        if values and 'email_to' in values:
            values['email_to'] = obj.obj.student_deposite_id.name.email
        m_id = self.pool.get('mail.mail').create(cr, uid, values)
        mail_id = self.pool.get('mail.mail').browse(cr,uid, m_id)
        if mail_id:
            mail_send_id = mail_id.send()
        return value

