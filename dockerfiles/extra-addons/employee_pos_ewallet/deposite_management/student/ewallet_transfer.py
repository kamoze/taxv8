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

from openerp import models, api,fields, _
from openerp.tools.translate import _
from openerp.exceptions import except_orm
from openerp import tools
import datetime


class FundTransfer(models.TransientModel):
    _name = "fund.transfer"
    """ New class for fund transfer functionality"""


    @api.depends('account_id')
    def _get_current_balanace(self):
        ## function field for getting balance value for current user
        student_pool = self.env['op.student']
        total_current_balance = 0.00
        for rec in self:
            student_ids = student_pool.search([('user_id','=',rec._uid)])
            for student_id in student_ids:
                if student_id.credit_limit>=0:
                    total_current_balance = student_id.credit_limit + student_id.stud_balance_amount
                else:
                    total_current_balance = student_id.stud_balance_amount
                # rec.account_id = student_id.ean13 or False
                rec.current_balance = total_current_balance or 0.00

    @api.one
    @api.constrains('description')
    def _check_description_count(self):
        """
            Apply constrains for description to accept only 50 char

        """

        for rec in self:
            if rec.description and len(rec.description)>50:
                raise except_orm(_('Warning!'),
                                 _("Description Lenght must be less than or equal to 50. "))

    account_id = fields.Char(string="Account ID")
    current_balance = fields.Float(compute="_get_current_balanace", string="Current Balance")
    amount_to_transfer = fields.Float(string="Amount To Transfer")
    description = fields.Text("Description")

    ##Or Selection field to select employee and student
    select_user = fields.Selection([('Student', 'Student'), ('Employee', 'Employee')], string="Select User",
                                   default='Student')
    student_id = fields.Many2one('op.student', 'Student')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    @api.multi
    ## this function open wizard for changing project dates
    def confirm_fund_transfer(self):
        self.ensure_one()
        ## Get view id
        model_data_obj = self.env['ir.model.data']
        student_pool = self.env['op.student']
        employee_pool = self.env['hr.employee']
        partner_obj = self.env['res.partner']

        ## Vlidation over amount for zero or -ve value
        if self.amount_to_transfer <= 0.00:
            raise except_orm(_('Warning!'),
                             _("You can't Transfer zero Amount/Less than zero Amount.!"))
        ## Validation over amount for always less than balance amount
        if self.amount_to_transfer > self.current_balance:
            raise except_orm(_('Warning!'),
                             _("Insufficient Balance."))

        ## Validation for account no if not present show warning
        student_id = student_pool.sudo().search([('ean13', '=', self.account_id)])

        if not student_id:
            employee_id = employee_pool.sudo().search([('ean13', '=', self.account_id)])
            if not employee_id:
                ## Search emp by  Student ID
                search_by_id_student_id = student_pool.sudo().search([('gr_no', '=', self.account_id)])
                if not search_by_id_student_id:
                    ## Search emp by  Employee ID
                    search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', self.account_id)])
                    if not search_by_id_employee_id:
                        raise except_orm(_('Warning!'),
                                         _("Beneficiary not found, Please input correct Number."))


        compose_form = self.env.ref('deposite_management.confirm_fund_transfer_form_view', False)
        ## return wizard after click on Fund Transfer Button
        return {
            'name': _('Fund Transfer Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fund.transfer.confirmation',
            'view_id': compose_form.id,
            'target': 'new',
        }
        # return True


class FundTransferConfirmation(models.Model):
    _name = "fund.transfer.confirmation"

    name = fields.Char('Beneficiary Name')
    photo = fields.Binary('Photo')
    account_no = fields.Char('Beneficiary Account No.')
    date = fields.Datetime('Date', default=datetime.datetime.now())
    amount_transfer = fields.Float('Amount To Transfer')
    description = fields.Text("Description")
    total_deposite_balance = fields.Float("After Deposte Total Balance")
    total_expense_balance = fields.Float("After Expense Total Balance")
    pass_employee_id = fields.Many2one('hr.employee', 'Employee')
    pass_student_id = fields.Many2one('op.student', 'Student')
    pin_varification = fields.Char('Enter PIN')

    def get_beneficiary_name(self, fund_transfer_info):
        ## function field for getting balance value for current user
        partner_obj = self.env['res.partner']
        student_pool = self.env['op.student']
        employee_pool = self.env['hr.employee']

        full_name = ""
        if fund_transfer_info.account_id:
            student_id = student_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])

            if student_id:
                full_name = student_id.last_name + '' + student_id.middle_name + '' + student_id.name
                # query = """select id, last_name, middle_name from op_student where partner_id=%s"""
                # self.env.cr.execute(query, (partner_id.id,))
                # query_results = self.env.cr.dictfetchall()
                # if query_results and 'last_name' in query_results[0]:
                #     full_name = query_results[0].get('last_name')
                # if query_results and 'middle_name' in query_results[0]:
                #     full_name = full_name + ' '  + query_results[0].get('middle_name')
                # if partner_id.name:
                #     full_name = full_name + ' ' + partner_id.name

                return full_name
            employee_id = employee_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])
            if employee_id:
                full_name = employee_id.name
                return full_name

            ## Search EMployee By Employee ID
            search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', fund_transfer_info.account_id)])
            if search_by_id_employee_id:
                full_name = search_by_id_employee_id.name
                return full_name
            ## Search by student matrix ID
            search_by_id_student_id = student_pool.sudo().search([('gr_no', '=', fund_transfer_info.account_id)])
            if search_by_id_student_id:
                full_name = search_by_id_student_id.last_name + '' + search_by_id_student_id.middle_name + '' + search_by_id_student_id.name
                return full_name

        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                full_name = employee_id.name
                return full_name
            if fund_transfer_info.student_id:
                student_id = student_pool.sudo().search([('id', '=', fund_transfer_info.student_id.id)])
                if student_id:
                    full_name = student_id.last_name + '' + student_id.middle_name + '' + student_id.name
                    return full_name


    def get_user_photo(self, fund_transfer_info):
        student_pool = self.env['op.student']
        employee_pool = self.env['hr.employee']

        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                return employee_id.image_medium
            if fund_transfer_info.student_id:
                student_id = student_pool.sudo().search([('id', '=', fund_transfer_info.student_id.id)])
                if student_id:
                    return student_id.photo


        student_id = student_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])
        if student_id:
            return student_id.photo

        employee_id = employee_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])
        if employee_id:
            return employee_id.image_medium

        search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', fund_transfer_info.account_id)])
        if search_by_id_employee_id:
            return search_by_id_employee_id.image_medium

        search_by_id_student_id = student_pool.sudo().search([('gr_no', '=', fund_transfer_info.account_id)])
        if search_by_id_student_id:
            return search_by_id_student_id.photo

    @api.model
    def default_get(self, fields):
        ## Function to open on wizard for activity completion record creation
        ## from project Milestones
        res = super(FundTransferConfirmation, self).default_get(fields)
        employee_pool = self.env['hr.employee']
        student_pool = self.env['op.student']
        active_id = self._context.get('active_id')
        fund_transfer_info = self.env['fund.transfer'].browse(active_id)
        beneficiary_name = self.get_beneficiary_name(fund_transfer_info)
        user_photo = self.get_user_photo(fund_transfer_info)
        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                account_no = employee_id.ean13
            elif fund_transfer_info.student_id:
                student_id = student_pool.sudo().search([('id', '=', fund_transfer_info.student_id.id)])
                account_no = student_id.ean13
        elif fund_transfer_info.account_id:
            account_no = fund_transfer_info.account_id
        if fund_transfer_info:
            res['photo'] = user_photo
            res['name'] = beneficiary_name
            res['account_no'] = account_no or False
            res['description'] = fund_transfer_info.description
            res['amount_transfer'] = fund_transfer_info.amount_to_transfer
            res['pass_employee_id'] = fund_transfer_info.employee_id.id or False
            res['pass_student_id'] = fund_transfer_info.student_id.id or False
        return res

    @api.multi
    def validate_current_user_pin(self, student_id):

        ## Logic to check validation over PIN
        if self.pin_varification:
            if student_id and self.pin_varification == student_id.pin:
                pass
            else:
                raise except_orm(_('Warning!'),
                                 _("Not a Valid PIN!"))

    @api.multi
    def call_transfer_fund(self):
        """ Write logic for transfering fund to give  account no. user """
        ## 1) Create expense line for current student
        ## 2) Create Deposite lines for oney transfer student

        ## 1
        student_pool = self.env['op.student']
        partner_obj = self.env['res.partner']
        employee_pool = self.env['hr.employee']

        if not self.pin_varification:
            raise except_orm(_('Warning!'),
                             _("Enter Valid PIN to proceed!"))


        student_id = student_pool.search([('user_id', '=', self._uid)])

        ## Validate Enter PIN
        if student_id:
            self.validate_current_user_pin(student_id)

        expense_vals = {
            'name': student_id.id,
            'amount': self.amount_transfer,
            'date': datetime.datetime.now(),
            'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s" % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
            'create_invoice': False,
            # 'student_id': student_id.id,
        }

        student_expenses_id = self.env['student.expenses'].sudo().create(expense_vals)
        self.total_expense_balance = student_id.stud_balance_amount

        ## Get employee form account id
        employee_id = employee_pool.sudo().search([('ean13', '=', self.account_no)])

        ## Search EMployee By Employee ID
        search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', self.account_no)])

        ## Search by student matrix ID
        search_by_id_student_id = student_pool.sudo().search([('gr_no', '=', self.account_no)])

        if not self.account_no:
            ## Logic for search by User Name
            employee_id = self.pass_employee_id.sudo()
            student_id = self.pass_student_id.sudo()
        else:
            ## Get partner form account id
            student_id = student_pool.sudo().search([('ean13', '=', self.account_no)])
        if student_id:
            deposite_vals = {
                'name': student_id.id,
                # 'amount': self.amount_to_transfer,
                'paid_amount': self.amount_transfer,
                'date': datetime.datetime.now(),
                'create_invoice': True,
            }
            student_deposite_id = self.env['student.deposits'].sudo().create(deposite_vals)
            if not self.account_no:
                trans_student_id = student_id.sudo()
            else:
                trans_student_id = student_pool.sudo().search([('ean13', '=', self.account_no)])
                if trans_student_id:
                    self.total_deposite_balance = trans_student_id.stud_balance_amount
        elif employee_id:
            deposite_vals = {
                'name': employee_id.id,
                'employee_id': employee_id.identification_id,
                'paid_amount': self.amount_transfer,
                'date': datetime.datetime.now(),
                'create_invoice': True,
                'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s " % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
            }
            employee_deposite_id = self.env['employee.deposits'].sudo().create(deposite_vals)
            self.total_deposite_balance = employee_id.available_balance

        elif search_by_id_employee_id:
            deposite_vals = {
                'name': search_by_id_employee_id.id,
                'employee_id': search_by_id_employee_id.identification_id,
                'paid_amount': self.amount_transfer,
                'date': datetime.datetime.now(),
                'create_invoice': True,
                'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s " % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
            }
            employee_deposite_id = self.env['employee.deposits'].sudo().create(deposite_vals)
            self.total_deposite_balance = search_by_id_employee_id.available_balance

        elif search_by_id_student_id:
            deposite_vals = {
                'name': search_by_id_student_id.id,
                'employee_id': search_by_id_student_id.gr_no,
                'paid_amount': self.amount_transfer,
                'date': datetime.datetime.now(),
                'create_invoice': True,
                'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s " % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
            }
            student_deposite_id = self.env['student.deposits'].sudo().create(deposite_vals)
            self.total_deposite_balance = search_by_id_student_id.stud_balance_amount

        # return True
        compose_form = self.env.ref('deposite_management.transfer_confirmation_popup_view', False)

        try:
            template_id = self.env.ref('deposite_management.email_template_student_fund_transfer', False)
        except ValueError:
            template_id = False
        values = self.env['email.template'].generate_email(template_id.id, self.id)

        ## Append Student email id to send mail
        if values and 'email_to' in values:
            values['email_to'] = student_id.sudo().email
        mail_id = self.env['mail.mail'].sudo().create(values)
        if mail_id:
            mail_send_id = mail_id.send()

        try:
            template_id_new = self.env.ref('deposite_management.email_template_student_fund_transfer_self_notification', False)
        except ValueError:
            template_id_new = False
        values_new = self.env['email.template'].generate_email(template_id_new.id, self.id)
        ## Append email id to send mail
        if values_new and 'email_to' in values_new:
            if student_id and trans_student_id:
                values_new['email_to'] = trans_student_id.email
            elif employee_id:
                values_new['email_to'] = employee_id.sudo().work_email
        mail_id_new = self.env['mail.mail'].sudo().create(values_new)
        if mail_id_new:
            mail_send_id = mail_id_new.send()
        ## return wizard after click on Fund Transfer Button
        return {
            'name': _('Fund Transfer Done'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fund.confirmation.msg',
            'view_id': compose_form.id,
            'target': 'new',
        }


class FundConfirmationMsg(models.TransientModel):
    _name = "fund.confirmation.msg"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    confirmation_msg = fields.Text("Confirmation Message", default="Transaction Successful!!")

    @api.multi
    def confirm_transfer_msg(self):
       return True


    @api.multi
    def confirm_transfer_msg_for_student(self):
        ir_model_data = self.env['ir.model.data']
        self.ensure_one()
        try:
            template_id = \
            ir_model_data.get_object_reference('deposite_management', 'email_template_student_fund_transfer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'fund.confirmation.msg',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "deposite_management.email_template_student_fund_transfer"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
