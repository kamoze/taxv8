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


class reconcile_employee_credit(osv.osv):
    _name = "reconcile.employee.credit"

    def emp_reconcile_overspend_amount_all(self, cr, uid, ids, context=None):
        """
            This function call from call
            this will check all deposite entries having paid invoices and Amount to Deposite > 0
        """

        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')

        ## Define object here
        acc_invoice_obj = self.pool.get('account.invoice')
        emp_deposite_obj = self.pool.get('employee.deposits')
        emp_obj = self.pool.get('hr.employee')
        models_data = self.pool.get('ir.model.data')

        ## search all employee with -ve balance
        employee_ids = emp_obj.search(cr, uid, [])
        for employee_id in emp_obj.browse(cr, uid, employee_ids):
            balance = employee_id.emp_balance_amount
            if balance < 0:
                deposite_vals = {
                    'name': employee_id.id,
                    'employee_id': employee_id.identification_id,
                    'paid_amount': abs(balance) or 0.00,
                    'date': datetime.datetime.now(),
                    'create_invoice': True,
                    'source': "Reconcile Overspend",
                }
                if context:
                    context.update({'credit_limit': employee_id.credit_limit})
                deposite_id = emp_deposite_obj.create(cr, uid, deposite_vals, context=context)
                if deposite_id:
                    if abs(balance) < 1:
                        raise osv.except_osv(_('Alert'), _("You can't create invoice with low amount."))
                    employee_id.emp_balance_amount = 0.00
        return True

