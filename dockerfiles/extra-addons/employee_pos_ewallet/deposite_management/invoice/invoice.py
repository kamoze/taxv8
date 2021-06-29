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
from openerp import SUPERUSER_ID

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
            "stud_deposit_id" : fields.many2one("student.deposits", "Student Deposit"),
            "employee_deposit_id": fields.many2one("employee.deposits", "Employee Deposit"),
            # "stud_matric_number": fields.related('student_id', 'gr_no', type='char', string='Student Matric Number'),

            # "couese_id": fields.related('student_id', 'course_id', type='many2one', relation='op.course',
            #                                  string='Course'),# store=True

            # "entry_session_id": fields.related('student_id', 'session_id', type='many2one', relation='op.sessions',
            #                         string='Entry Session'),
            #
            # "semester_id": fields.related('student_id', 'batch_id', type='many2one', relation='op.batch',
            #                                string='Semester'),

        }


class account_voucher(osv.osv):
    _inherit = "account.voucher"

    _columns = {
        # "stud_matric_number": fields.related('student_id', 'gr_no', type='char', string='Student Matric Number'),
        #
        # "couese_id": fields.related('student_id', 'course_id', type='many2one', relation='op.course',
        #                             string='Course'),  # store=True
        #
        # "entry_session_id": fields.related('student_id', 'session_id', type='many2one', relation='op.sessions',
        #                                    string='Entry Session'),
        #
        # "semester_id": fields.related('student_id', 'batch_id', type='many2one', relation='op.batch',
        #                               string='Semester'),
    }

    def button_proforma_voucher(self, cr, uid, ids, context):
        rtn_values = super(account_voucher, self).button_proforma_voucher(cr, uid, ids, context)
        if "invoice_id" in context:
            invoice = self.pool("account.invoice").browse(cr, uid, context['invoice_id'])
            if invoice.stud_deposit_id.id:
                context['account_voucher_id'] = ids
                self.pool("student.deposits").paid_invoice(cr, uid, [invoice.stud_deposit_id.id], context)
            elif invoice.employee_deposit_id.id:
                context['account_voucher_id'] = ids
                self.pool("employee.deposits").paid_invoice(cr, uid, [invoice.employee_deposit_id.id], context)

        uid = SUPERUSER_ID
        # stud_pool = self.pool.get('op.student')
        email_cc = ''
        obj = self.browse(cr, uid, ids[0])
        report_obj = self.pool.get('report')
        #pdf = report_obj.get_pdf(cr, uid, ids, 'deposite_management.report_receipt', data=None, context=context)
       # print "sssssssssss", pdf
        attachment_ids = []
        att_obj = self.pool.get('ir.attachment')
        attachment_data = {
            'name': "Report Data",
            'datas_fname': 'Receipt.pdf',  # your object File Name
            'type': 'binary',
            'res_model': 'account.voucher',
            #'db_datas': pdf
        }
        attachment_ids.append(att_obj.create(cr, uid, attachment_data, context=context))
        ir_model_data = self.pool.get('ir.model.data')
        email_template_pool = self.pool.get("email.template")
        template_id = False
        # template_id = ir_model_data.get_object_reference(cr, uid, 'deposite_management', 'account_voucher_receipt_report_sent_to_parent')[1]
        # student_id = stud_pool.search(cr, uid, [('partner_id', '=', obj.partner_id.id)])
        # student_info = stud_pool.browse(cr, uid, student_id)
        # for parent_id in student_info.parent_ids:
        #     if parent_id.guardians_email:
        #         email_cc += parent_id.guardians_email + ','
        #
        # mail_mail = self.pool.get('mail.mail')
        # email_template_pool.write(cr, uid, template_id, {'attachment_ids': [(6, 0, attachment_ids)],'email_cc': email_cc})
        # mail_id = email_template_pool.send_mail(cr, SUPERUSER_ID, template_id, ids[0], context=context)
        # mail_queue = mail_mail.process_email_queue(cr, SUPERUSER_ID, [mail_id])
        # msg_id = email_template_pool.send_mail(cr, uid, template_id, ids[0], context=context)

        return rtn_values



