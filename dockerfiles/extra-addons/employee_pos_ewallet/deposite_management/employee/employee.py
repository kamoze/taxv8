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
from datetime import timedelta
from openerp import SUPERUSER_ID
from lxml import etree
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from openerp.osv.orm import setup_modifiers


class employee_deposits(osv.osv):
    _name = "employee.deposits"
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    def emp_update_credit_amount(self, cr, uid, context=None):
        """
            This function call from call
            this will check all deposite entries having paid invoices and Amount to Deposite > 0
        """

        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')

        ## Define object here
        acc_invoice_obj = self.pool.get('account.invoice')
        emp_deposite_ids = self.search(cr, uid, [('amount', '>', 0.00)])
        for emp_deposite_id in self.browse(cr, uid, emp_deposite_ids):
            invoice_ids = acc_invoice_obj.search(cr, uid, [('employee_deposit_id', '=', emp_deposite_id.id), ('state', '=', 'paid')])
            if invoice_ids:
                ## Update employee deposite records
                self.write(cr, uid, emp_deposite_id.id, {'paid_amount': emp_deposite_id.amount, 'amount': 0.00})
                try:
                    template_id = ir_model_data.get_object_reference(cr, uid, 'employee_pos_ewallet',
                                                                     "schedular_reconcilation_email_notification_for_emp")[1]
                except ValueError:
                    raise osv.except_osv(_('Configuration Missing!'), _("Email Template not found!"))
                msg_id = email_template_pool.send_mail(cr, uid, template_id, emp_deposite_id.id)
                mail_queue = mail_mail.process_email_queue(cr, uid, [msg_id])
        return True



    def _get_emp_no(self, cr, uid, ids, field_name, arg, context={}):
        res= {}
        for id in self.browse(cr, uid, ids):
            res[id.id] = id.name.id and id.name.identification_id or None
        return res

    def create(self, cr, uid, vals, context=None):

        ## Hide for now as we are not checking credit limit ----> checking available balace
        # if context and 'credit_limit' in context and 'paid_amount' in vals:
        #     if context.get('credit_limit') < vals.get('paid_amount'):
        #         raise osv.except_osv(_('Alert'), _("Insufficiant balance."))
        if context is None:
            context = {}
        res = super(employee_deposits, self).create(cr, uid, vals, context=context)
        return res

#     def get_balance_detail(self, cr, uid, ids, field_name, arg, context=None):
#         res= {}
#         for id in self.browse(cr, uid, ids):
#             total_credit, total_debit = 0.0, 0.0
#             for credit in self.browse(cr, uid, self.search(cr, uid, [('name','=', id.name.id)])):
#                 total_credit += credit.paid_amount
#             debit_obj = self.pool("employee.expenses")
#             for debit in debit_obj.browse(cr, uid, debit_obj.search(cr, uid, [('name','=',id.name.id)])):
#                 total_debit += debit.amount
#             res[id.id] = total_credit - total_debit
#         return res


    def _get_default_emp(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        employee = emp_obj.search(cr, SUPERUSER_ID, [('user_id', '=', uid)])
        for employee_id in emp_obj.browse(cr, uid, employee):
            return employee_id.id

    _columns = {
        "name": fields.many2one("hr.employee","Employee"),
        "amount": fields.float("Amount to Deposit", track_visibility="onchange"),
        "paid_amount": fields.float("Credited Amount", track_visibility="onchange"),
        "date": fields.datetime("Date Created", default=datetime.datetime.now(), track_visibility="onchange"),
        "create_invoice": fields.boolean("Is create invoice?", track_visibility="onchange"),
        "employee_id":fields.function(_get_emp_no, type="char", string="Employee ID", size=15),
        #"emp_balance_amount": fields.function(get_balance_detail, type="float", string="Balance"),
        "source": fields.char("Description", track_visibility="onchange"),
        'create_date': fields.datetime("Date Created"),
    }

    _defaults = {
        'name': _get_default_emp
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):
        """
            To set access right for Credit limit fields
            only edict by account manager and can view by other user
        """
        res = super(employee_deposits, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                                       toolbar=toolbar, submenu=submenu)
        context = context or {}
        result = \
        finance_grp_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_account_manager')[1]
        user_group_ids = self.pool.get('res.users').browse(cr, uid,uid).groups_id.ids
        if view_type == 'form':
            doc = etree.XML(res['arch'], parser=None, base_url=None)
            if finance_grp_id in user_group_ids:
                # first_node = doc.xpath("//page[@name='name']")
                for node in doc.xpath("//field[@name='name']"):
                    node.set('readonly', '0')
            else:
                for node in doc.xpath("//field[@name='name']"):
                    node.set('readonly', '1')
                setup_modifiers(node, res['fields']['name'])
                res['arch'] = etree.tostring(doc, encoding="utf-8")
        return res

    def act_invoice_pay_in_emp(self, cr, uid, ids, context=None):

        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet', 'pay_in_employee_form')


        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.pay.in.wiz',
            'view_id': False,
            'views': [(form_view and form_view[1] or False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True
        }


    def act_invoice_deposite(self, cr, uid, ids, context=None):
        uid = 1
        obj = self.browse(cr, uid, ids[0])
        if obj.amount < 1:
             raise osv.except_osv(_('Alert'),_("You can't create invoice with low amount."))
        invoice_lines = [[0, False, {'name':"E-wallet Fund", 'price_unit':obj.amount, 'quantity':1.0}]]
        invoice_obj, invoice_id = self.pool.get('account.invoice'), None
        onchange_partner = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice', obj.name.user_id.partner_id.id)
        default_fields = invoice_obj.fields_get(cr, uid, context)
        invoice_default = invoice_obj.default_get(cr, uid, default_fields, context)
        onchange_partner['value']['partner_id'] = obj.name.user_id.partner_id.id
        onchange_partner['value']['invoice_line'] = invoice_lines
        onchange_partner['value']['employee_deposit_id'] = obj.id
        invoice_default.update(onchange_partner['value'])
        invoice_id = invoice_obj.create(cr, uid, invoice_default)
        invoice_obj.signal_workflow(cr, uid, [invoice_id],'invoice_open')
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
        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')
        attachment_ids = []
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'employee_pos_ewallet', "email_template_employee_deposite_invoice")[1]
        except ValueError:
            raise osv.except_osv(_('Configuration Missing!'),_("Email Template not found!"))
        report_obj = self.pool.get('report')
        pdf = report_obj.get_pdf(cr, uid, [invoice_id], 'account.report_invoice', data=None, context=context)

        att_obj = self.pool.get('ir.attachment')
        attachment_data = {
            'name': "Invoice",
            'datas_fname':'Invoice.pdf', # your object File Name
            'type':'binary',
            'res_model':'op.admission',
            'db_datas':pdf
                }
        attachment_ids.append (att_obj.create(cr, uid, attachment_data, context=context))
        email_template_pool.write(cr,uid,template_id,{'attachment_ids':[(6, 0, attachment_ids)]})
        msg_id = email_template_pool.send_mail(cr, uid, template_id, ids[0], context=context)
        mail_queue=mail_mail.process_email_queue(cr, uid, [msg_id])
        self.write(cr, uid, ids, {'create_invoice':True})
        return value


    def list_of_accounts(self, cr, uid, ids, context):
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        tree_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        value = {
                'domain': str([('employee_deposit_id', 'in', ids)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'view_id': False,
                'views': [(tree_view and tree_view[1] or False, 'tree'),
                          (form_view and form_view[1] or False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'nodestroy': True
            }
        return value

    def paid_invoice(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids[0], context)
        if "account_voucher_id" in context:
            av_obj = self.pool['account.voucher'].browse(cr, uid, context['account_voucher_id'])[0]
            pamt = obj.paid_amount + av_obj.amount
            ramt = obj.amount - av_obj.amount
            self.write(cr, uid, ids[0], {'amount':ramt,'paid_amount':pamt})
        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'employee_pos_ewallet', "email_template_employee_deposite_funded")[1]
        except ValueError:
            raise osv.except_osv(_('Configuration Missing!'),_("Email Template not found!"))
        msg_id = email_template_pool.send_mail(cr, uid, template_id, ids[0], context=context)
        mail_queue=mail_mail.process_email_queue(cr, uid, [msg_id])
        return True


    def get_localised_date(self, cr, uid, ids, create_date, days=0, return_datetime=False):
        ''' Function return next localized date based on days passed from source. -1 for yesterday, +1 for tomorrow, 0 for today '''
        #Timezoneconversion
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        deposite_id = self.browse(cr, uid, ids, context=None)
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone('Africa/Lagos') or pytz.utc
        #Finding next date(Localized) based on days passed
        next_date = deposite_id.create_date + timedelta(days=days)
        next_date = pytz.utc.localize(next_date, is_dst=None)
        next_date = datetime.strptime(next_date.astimezone(tz).strftime( DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
        if return_datetime:
            return next_date
        return next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)


class employee_expenses(osv.osv):
    _name = "employee.expenses"
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    def _get_emp_no(self, cr, uid, ids, field_name, arg, context={}):
        res= {}
        for id in self.browse(cr, uid, ids):
            res[id.id] = id.name.id and id.name.identification_id or None
        return res





    _columns = {
        "name": fields.many2one("hr.employee","Employee"),
        "amount": fields.float("Debited Amount", track_visibility="always"),
        "date": fields.datetime("Date Created", default=datetime.datetime.now(), track_visibility="always"),
        "source": fields.char("Source", track_visibility="always"),
        "create_invoice": fields.boolean("Is create invoice?", track_visibility="always"),
        "employee_id":fields.function(_get_emp_no, type="char", string="Employee ID", size=15),
    }


class hr_employee(osv.osv):
    _inherit = "hr.employee"


    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        ## Logic to search all employees under specific employee
        ## For transfer money by Name
        user = SUPERUSER_ID
        ids = []
        if not args:
            args = []

        if name:
            if name:
                args += [('name', operator, name)]

        if not context:
            context = {}

        ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context)
        return result



    def fields_view_get(self, cr, uid, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):
        """
            To set access right for Credit limit fields
            only edict by account manager and can view by other user
        """
        res = super(hr_employee, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context,
                                                       toolbar=toolbar, submenu=submenu)
        context = context or {}
        if view_type == 'form' and context.get('Followupfirst'):
            doc = etree.XML(res['arch'], parser=None, base_url=None)
            first_node = doc.xpath("//page[@name='followup_tab']")
            root = first_node[0].getparent()
            root.insert(0, first_node[0])
            res['arch'] = etree.tostring(doc, encoding="utf-8")
        return res



    def get_balance_detail(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        uid = SUPERUSER_ID
        for id in self.browse(cr, uid, ids):
            total_credit, total_debit = 0.0, 0.0
            for credit in id.employee_deposit_ids:
                total_credit += credit.paid_amount
            debit_obj = self.pool("employee.expenses")
            for debit in debit_obj.browse(cr, uid, debit_obj.search(cr, uid, [('name','=',id.id)])):
                total_debit += debit.amount
            res[id.id] = total_credit - total_debit
        return res

    def get_total_expense(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uid = SUPERUSER_ID
        for id in self.browse(cr, uid, ids):
            total_debit = 0.0
            debit_obj = self.pool("employee.expenses")
            for debit in debit_obj.browse(cr, uid, debit_obj.search(cr, uid, [('name','=',id.id)])):
                total_debit += debit.amount
            res[id.id] = total_debit
        return res

    def get_available_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uid = SUPERUSER_ID
        for id in self.browse(cr, uid, ids):
            available_balance = id.credit_limit + id.emp_balance_amount
            ## set available_balance to zero if total balance in -ve
            if available_balance < 0.00:
                res[id.id] = 0.00
            else:
                res[id.id] = available_balance
        return res

    _columns={
          "employment_date": fields.date("Date of Employment"),
          "next_of_kin_name": fields.char("Next of Kin Name", size=65),
          "next_of_kin_number": fields.char("Next of Kin Number", size=65),
          "next_of_kin_address": fields.text("Next of Kin Address"),
          "relationship": fields.char("Relationship", size=65),
          "employee_deposit_ids": fields.one2many("employee.deposits", "name", "E-Wallet Employee Deposit"),
          "employee_expenses_ids": fields.one2many("employee.expenses", "name", "E-Wallet Employee Expenses"),
          "emp_balance_amount": fields.function(get_balance_detail, type="float", string="Balance"),
          "total_expense": fields.function(get_total_expense, type="float", string="Total Expenses"),
          "credit_limit": fields.float(string="Credit Limit"),
          "available_balance": fields.function(get_available_balance, type="float",
                                               string="Available Balance"),
    }

    def confirm_employee_reconcile_overspend(self, cr, uid, ids, context=None):
        """ Function to reconcile credit limit """

        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'employee_pos_ewallet',
                                                     'employee_reconcile_overspend_form_view')

        return {
            'name': _('Reconcile OverSpend'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.reconcile.overspend',
            'view_id': form_view[1],
            'target': 'new',
        }


