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


class employee_reconcile_overspend(osv.osv):
    _name = "employee.reconcile.overspend"

    def _get_current_credeit_limt(self, cr, uid, ids, context=None):
        return True

    def default_get(self, cr, uid, fields, context=None):
        res = super(employee_reconcile_overspend, self).default_get(cr, uid, fields, context=context)
        uid = SUPERUSER_ID
        emp_pool = self.pool.get('hr.employee')
        if context and 'active_id' in context:
            active_id = emp_pool.search(cr, uid, [('id', '=', context.get('active_id'))])
            employee_id = emp_pool.browse(cr, uid, active_id)
            if employee_id and employee_id.emp_balance_amount >=0:
                raise osv.except_osv(_('Alert'), _("You still have a Positive balance."))

            if employee_id:
                res['employee_id'] = employee_id.id,
                res['renaming_balance'] = str(employee_id. available_balance),
                res['amount_to_reconcile'] = str(employee_id.emp_balance_amount),

        return res

    _columns = {
        'employee_id': fields.many2one('hr.employee', string="Employee"),
        'renaming_balance': fields.char('Balance'),
        'amount_to_reconcile': fields.char('Amount'),
    }

    def pay_employee_reconcile_overspend(self, cr, uid, ids, context=None):
        """ Create -ve Deposite lines for reconcile overspend and expense lines for same """

        obj = self.browse(cr, uid, ids[0])
        uid = SUPERUSER_ID
        value = {}
        emp_deposite = self.pool.get('employee.deposits')
        emp_expesne = self.pool.get('employee.expenses')
        if obj:
            balance = obj.employee_id.emp_balance_amount


            if balance < 0:
                ## Not required for now
                # ## Create expese for credit limit
                # expense_vals = {
                #     'name': obj.employee_id.id,
                #     'employee_id': obj.employee_id.identification_id,
                #     'amount': balance,
                #     'date': datetime.datetime.now(),
                #     'source': "Reconcile Overspend",
                #     'create_invoice': False,
                # }
                # expense_id = emp_expesne.create(cr, uid, expense_vals)

                deposite_vals = {
                    'name': obj.employee_id.id,
                    'employee_id': obj.employee_id.identification_id,
                    'amount': abs(balance) or 0.00,
                    'date': datetime.datetime.now(),
                    'create_invoice': True,
                    'source': "Reconcile Overspend",
                    }
                if context:
                    context.update({'credit_limit':obj.employee_id.credit_limit})
                deposite_id = emp_deposite.create(cr, uid, deposite_vals,context=context)

                if deposite_id:
                    if abs(balance) < 1:
                        raise osv.except_osv(_('Alert'), _("You can't create invoice with low amount."))

                    ## Comment this code because no need to take amount form credit limt
                    ## Modified logic
                    # obj.employee_id.credit_limit = obj.employee_id.credit_limit - abs(balance)
                    ##
                    obj.employee_id.emp_balance_amount = 0.00
                    invoice_lines = [
                        [0, False, {'name': "Reconcile Overspend", 'price_unit': abs(balance), 'quantity': 1.0}]]
                    invoice_obj, invoice_id = self.pool.get('account.invoice'), None
                    onchange_partner = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice',
                                                                       obj.employee_id.user_id.partner_id.id)
                    default_fields = invoice_obj.fields_get(cr, uid, context)
                    invoice_default = invoice_obj.default_get(cr, uid, default_fields, context)
                    onchange_partner['value']['partner_id'] = obj.employee_id.user_id.partner_id.id
                    onchange_partner['value']['invoice_line'] = invoice_lines
                    onchange_partner['value']['employee_deposit_id'] = deposite_id
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

            #
        return value

