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



class EmployeeFundTransfer(models.TransientModel):
    _name = "employee.fund.transfer"
    """ New class for fund transfer functionality For Employee"""


    @api.depends('account_id')
    def _get_current_balanace(self):
        ## function field for getting balance value for current user
        employee_pool = self.env['hr.employee']
        resource_obj = self.env['resource.resource']
        total_current_balance = 0.00
        for rec in self:
            resource_id = resource_obj.search([('user_id', '=', rec._uid)])[0]
            if resource_id:
                employee_ids = employee_pool.search([('resource_id', '=', resource_id.id)])
                for employee_id in employee_ids:
                    if employee_id.credit_limit>=0:
                        total_current_balance = employee_id.credit_limit + employee_id.emp_balance_amount
                    else:
                        total_current_balance = employee_id.emp_balance_amount
                    rec.current_balance = total_current_balance or 0.00

    @api.one
    @api.constrains('description')
    def _check_description_count(self):
        """
            Apply constrains for description to accept only 50 char

        """
        for rec in self:
            if rec.description and len(rec.description) > 50:
                raise except_orm(_('Warning!'),
                                 _("Description Lenght must be less than or equal to 50. "))



    account_id = fields.Char(string="Account ID")
    current_balance = fields.Float(compute="_get_current_balanace", string="Current Balance")
    amount_to_transfer = fields.Float(string="Amount To Transfer")
    description = fields.Text("Description")
    ##Or Selection field to select employee and student
    select_user = fields.Selection([('Employee','Employee')], string="Select User", default='Employee')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    @api.multi
    def confirm_fund_transfer(self):
        ## this function open wizard for changing project dates
        self.ensure_one()
        ## Get view id
        model_data_obj = self.env['ir.model.data']
        employee_pool = self.env['hr.employee']

        ## Define variable for current blance

        ## Vlidation over amount for zero or -ve value
        if self.amount_to_transfer <= 0.00:
            raise except_orm(_('Warning!'),
                             _("You can't Transfer zero Amount/Less than zero Amount.!"))
        ## Validation over amount for always less than balance amount
        if self.amount_to_transfer > self.current_balance:
            raise except_orm(_('Warning!'),
                             _("Insufficient Balance."))

        ## Validation for account no if not present show warning
        employee_id = employee_pool.sudo().search([('ean13','=',self.account_id)])
        if not employee_id:
            ## Validation for account no if not present show warning for student
            # student_id = student_pool.sudo().search([('ean13', '=', self.account_id)])
            # if not student_id:
                ## Search emp by  Employee ID
            earch_by_id_employee_id = employee_pool.sudo().search([('identification_id','=',self.account_id)])
            if not earch_by_id_employee_id:
                    ## Search by student matrix ID
                search_by_id_student_id = []#student_pool.sudo().search([('gr_no', '=', self.account_id)])
                if not search_by_id_student_id:
                    raise except_orm(_('Warning!'),
                            _("Beneficiary not found, Please input correct Number."))




        compose_form = self.env.ref('employee_pos_ewallet.employee_confirm_fund_transfer_form_view', False)
        ## return wizard after click on Fund Transfer Button
        return {
            'name': _('Fund Transfer Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.fund.transfer.confirmation',
            'view_id': compose_form.id,
            'target': 'new',
        }
        return  True


class EmployeeFundTransferConfirmation(models.Model):
    _name = "employee.fund.transfer.confirmation"

    name = fields.Char('Beneficiary Name')
    photo = fields.Binary('Photo')
    account_no = fields.Char('Beneficiary Account No.')
    date = fields.Datetime('Date')
    amount_transfer = fields.Float('Amount To Transfer')
    description = fields.Text("Description")
    total_expense_balance = fields.Float("Total Expense Balance")
    total_deposite_balance = fields.Float("Total Deposite Balance")
    pass_employee_id = fields.Many2one('hr.employee', 'Employee')
    # pass_student_id = fields.Many2one('op.student', 'Student')

    ## PIN varification
    pin_varification = fields.Char('Enter PIN')

    def get_beneficiary_name(self, fund_transfer_info):
        ## function field for getting balance value for current user
        employee_pool = self.env['hr.employee']
        full_name = ""
        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                if employee_id:
                    full_name = employee_id.name
        if fund_transfer_info.account_id:
            employee_id = employee_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])
            if employee_id:
                full_name = employee_id.name
            ## Search EMployee By Employee ID
            search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', fund_transfer_info.account_id)])
            if search_by_id_employee_id:
                full_name = search_by_id_employee_id.name
            ## Search by student matrix ID

        return full_name


    def get_user_photo(self, fund_transfer_info):
        employee_pool = self.env['hr.employee']

        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                return employee_id.image_medium
            # if fund_transfer_info.student_id:
            #     return fund_transfer_info.student_id.photo
        employee_id = employee_pool.sudo().search([('ean13', '=', fund_transfer_info.account_id)])
        if employee_id:
            return employee_id.image_medium

        search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', fund_transfer_info.account_id)])
        if search_by_id_employee_id:
            return search_by_id_employee_id.image_medium

    @api.model
    def default_get(self, fields):
        ## Function to open on wizard for activity completion record creation
        res = super(EmployeeFundTransferConfirmation, self).default_get(fields)
        employee_pool = self.env['hr.employee']
        active_id = self._context.get('active_id')
        fund_transfer_info = self.env['employee.fund.transfer'].browse(active_id)
        beneficiary_name = self.get_beneficiary_name(fund_transfer_info)
        user_photo = self.get_user_photo(fund_transfer_info)
        if not fund_transfer_info.account_id:
            if fund_transfer_info.employee_id:
                employee_id = employee_pool.sudo().search([('id', '=', fund_transfer_info.employee_id.id)])
                account_no = employee_id.ean13
            # elif fund_transfer_info.student_id:
            #     account_no = fund_transfer_info.student_id.ean13
        elif fund_transfer_info.account_id:
            account_no = fund_transfer_info.account_id
        if fund_transfer_info:
            res['photo'] = user_photo
            res['name'] = beneficiary_name
            res['account_no'] = account_no
            res['description'] = fund_transfer_info.description
            res['amount_transfer'] = fund_transfer_info.amount_to_transfer
            res['pass_employee_id'] = fund_transfer_info.employee_id.id or False

        return res

    @api.multi
    def validate_current_user_pin(self, employee_id):

        ## Logic to check validation over PIN
        if self.pin_varification:
            if employee_id and self.pin_varification == employee_id.pin:
                pass
            else:
                raise except_orm(_('Warning!'),
                                 _("Not a Valid PIN!"))


    @api.multi
    def call_transfer_fund(self):
        """ Write logic for transfering fund to give  account no. user """
        ## 1) Create expense line for current staff
        ## 2) Create Deposite lines for oney transfer staff

        ## 1
        employee_pool = self.env['hr.employee']
        resource_obj = self.env['resource.resource']

        if not self.pin_varification:
            raise except_orm(_('Warning!'),
                             _("Enter Valid PIN to proceed!"))

        resource_id = resource_obj.sudo().search([('user_id', '=', self._uid)])[0]
        if resource_id:
            employee_id = employee_pool.sudo().search([('resource_id', '=', resource_id.id)])

            ## Validate Enter PIN
            if employee_id:
                self.validate_current_user_pin(employee_id)

            if employee_id:
                expense_vals = {
                    'name': employee_id.id,
                    'employee_id': employee_id.identification_id,
                    'amount': self.amount_transfer,
                    'date': datetime.datetime.now(),
                    'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s" % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
                    'create_invoice': False,
                }

                employee_expenses_id = self.env['employee.expenses'].sudo().create(expense_vals)
                self.total_expense_balance = employee_id.available_balance
                try:
                    template_id = self.env.ref(
                        'employee_pos_ewallet.email_template_employee_fund_transfer_self_notification', False)
                except ValueError:
                    template_id = False
                values = self.env['email.template'].generate_email(template_id.id, self.id)
                ## Append emial id
                if values and 'email_to' in values:
                    if employee_id:
                        values['email_to'] = employee_id.sudo().work_email
                mail_id = self.env['mail.mail'].sudo().create(values)
                if mail_id:
                    mail_send_id = mail_id.send()


        if self.account_no:
            ## Get employee form account id
            employee_id = employee_pool.sudo().search([('ean13', '=', self.account_no)])
            ## Search EMployee By Employee ID
            search_by_id_employee_id = employee_pool.sudo().search([('identification_id', '=', self.account_no)])

        if not self.account_no:
            ## Logic for search by User Name
            employee_id = self.pass_employee_id.sudo()
            # student_id = self.pass_student_id.sudo()

        if employee_id:
            deposite_vals = {
                'name': employee_id.id,
                'employee_id': employee_id.identification_id,
                'paid_amount': self.amount_transfer,
                'date': datetime.datetime.now(),
                'create_invoice': True,
                'source': "Transfer Amount of %s to account no %s (%s) on date %s - %s" % (self.amount_transfer, self.account_no, self.name, datetime.datetime.now(), self.description),
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


        compose_form = self.env.ref('employee_pos_ewallet.employee_transfer_confirmation_popup_view', False)


        try:
            template_id = self.env.ref('employee_pos_ewallet.email_template_employee_fund_transfer', False)
        except ValueError:
            template_id = False
        values = self.env['email.template'].generate_email(template_id.id, self.id)
        ## Append employee emial id
        if values and 'email_to' in values:
            if employee_id:
                values['email_to'] = employee_id.work_email
        mail_id = self.env['mail.mail'].create(values)
        if mail_id:
            mail_send_id = mail_id.send()



        return {
            'name': _('Fund Transfer Done'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fund.confirmation.msg',
            'view_id': compose_form.id,
            'target': 'new',
        }

    def _get_default_date(self, cr, uid, context=None):
        date = datetime.datetime.now(),
        if date:
            return date

    _defaults = {
        'name': _get_default_date
    }

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.constrains('ean13')
    def _check_partner_ean_no(self):
        """
            Apply constrains for EAN13 code to accept only
            unique values
        """
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([])
        ean_list = []
        employee_ids = self.search([('id', '!=', self.id)])
        ## get EAN for Employee
        for employee_id in employee_ids:
            if employee_id.ean13:
                ean_list.append(employee_id.ean13)
        ## Get EAN for Partner
        for partner_id in partner_ids:
            if partner_id.ean13:
                ean_list.append(partner_id.ean13)

        if self.ean13 in ean_list:
            raise except_orm(_('Warning!'),
                             _("A EAN Code can\'t have duplicate values."))

    api.constrains('pin')
    def pin_range(self):
        for each in self:
            if each.pin:
                if len(each.pin) < 4 or len(each.pin) > 4:
                    raise except_orm(_('Warning'),
                                     _("Please enter 4 digit pin only."))

    pin = fields.Char('PIN')
    ean13 = fields.Char('EAN13')

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
            ir_model_data.get_object_reference('employee_pos_ewallet', 'email_template_student_fund_transfer')[1]
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
            'custom_layout': "employee_pos_ewallet.email_template_student_fund_transfer"
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

