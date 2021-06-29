# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-TODAY Acespritech Solutions Pvt Ltd
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
##############################################################################
from openerp import models, fields, api,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time


class wizard_customer_deposit(models.TransientModel):
    _name = 'wizard.customer.deposit'

    partner_id = fields.Many2one('res.partner', 'Customer',
                                 domain="[('customer','=',True)]", required=True)
    amount = fields.Float('Amount', required=True)

    def make_deposit(self, company, partner, amount):
        mv_obj = self.env['account.move']
        journal_id = company.deposit_journal_id and company.deposit_journal_id.id or False
        ctx = dict(self._context)
        ctx['company_id'] = company.id
        period_id = self.env['account.period'].find(fields.date.today(), context=ctx)[0]
        if not journal_id:
            raise Warning(_('No Deposit Journal!'),
                          _('Please configure deposit journal into company.'))
        dr_line = {
            'name': 'Deposit Amount',
            'partner_id': partner.id,
            'debit': self.amount,
            'account_id': company.deposit_journal_id.default_credit_account_id.id,
            'date': time.strftime('%Y-%m-%d'),
            'period_id': period_id.id
        }
        cr_line = {
            'name': partner.name,
            'partner_id': partner.id,
            'credit': amount,
            'account_id': partner.property_account_payable.id,
            'date': time.strftime('%Y-%m-%d'),
            'period_id': period_id.id
        }
        move = {
            'journal_id': journal_id,
            'period_id': period_id.id,
            'line_id': [(0, 0, cr_line), (0 , 0, dr_line)]
        }
        move_id = mv_obj.create(move)
        move_id.button_validate()
        self.env['customer.deposit'].create({'partner_id': partner.id,
                                             'amount': amount,
                                             'user_id': ctx.get('uid')})
        return True

    @api.multi
    def action_deposit(self):
        """
        Deposit amount (credit) for selected customer.
        :return:
        """
        if self._context and self._context.get('uid'):
            user = self.env['res.users'].browse(self._context.get('uid'))
            self.make_deposit(user.company_id, self.partner_id, self.amount)
        return {'type': 'ir.actions.act_window_close'}
