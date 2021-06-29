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


class student_reconcile_employee_credit(osv.osv):
    _name = "student.reconcile.employee.credit"


    def student_update_credit_amount_button(self, cr, uid, ids, context=None):
        """
            This function call from call
            this will check all deposite entries having paid invoices and Amount to Deposite > 0
        """

        ## Define object here
        acc_invoice_obj = self.pool.get('account.invoice')
        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        mail_mail = self.pool.get('mail.mail')
        student_deposite_obj = self.pool.get('student.deposits')

        student_deposite_ids = student_deposite_obj.search(cr, uid, [('amount', '>', 0.00)])
        for student_deposite_id in student_deposite_obj.browse(cr, uid, student_deposite_ids):
            invoice_ids = acc_invoice_obj.search(cr, uid, [('stud_deposit_id', '=', student_deposite_id.id), ('state', '=', 'paid')])
            if invoice_ids:
                student_deposite_obj.write(cr, uid, student_deposite_id.id, {'paid_amount': student_deposite_id.amount, 'amount': 0.00})
                try:
                    template_id = ir_model_data.get_object_reference(cr, uid, 'deposite_management', "schedular_reconcilation_email_notification_for_student")[1]
                except ValueError:
                    raise osv.except_osv(_('Configuration Missing!'), _("Email Template not found!"))
                msg_id = email_template_pool.send_mail(cr, uid, template_id, student_deposite_id.id)
                mail_queue = mail_mail.process_email_queue(cr, uid, [msg_id])
        return True
