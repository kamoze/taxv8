# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round as round


class account_voucher(models.Model):
    _inherit = 'account.voucher'

    def get_invoice(self):
        invoice_details_list = []
        if self.ids:
            data = self.ids
            inv_lst = []
            inv_obj = self.pool.get('account.invoice')
            voucher_obj = self.pool.get('account.voucher')
            obj_precision = self.pool.get('decimal.precision')
            prec = obj_precision.precision_get(self._cr, SUPERUSER_ID, 'Account')
            for cr1 in voucher_obj.browse(self._cr, SUPERUSER_ID, self._ids).line_cr_ids:
                if cr1.move_line_id and cr1.move_line_id.invoice:
                    inv_lst.append(cr1.move_line_id.invoice.id)
        return inv_lst

    def get_invoice_information1(self):
        invoice_details_list = []
        if self.ids:
            data = self.ids
            inv_lst = []
            inv_obj = self.pool.get('account.invoice')
            voucher_obj = self.pool.get('account.voucher')
            obj_precision = self.pool.get('decimal.precision')
            prec = obj_precision.precision_get(self._cr, SUPERUSER_ID, 'Account')
            cr_ln = voucher_obj.browse(self._cr, SUPERUSER_ID, self._ids).line_cr_ids
            is_reconcile_invoice = []
            if len(cr_ln) == 1:
                for cr1 in cr_ln:
                    if cr1.move_line_id and cr1.move_line_id.invoice:
                        if cr1.reconcile == True:
                            is_reconcile_invoice.append(cr1.move_line_id.invoice.id)
                        inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile_invoice.append(cr1.move_line_id.invoice.id)
            else:
                for cr1 in cr_ln:
                    if cr1.reconcile == True:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            is_reconcile_invoice.append(cr1.move_line_id.invoice.id)
                            inv_lst.append(cr1.move_line_id.invoice.id)
                    else:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile_invoice.append(cr1.move_line_id.invoice.id)

            if len(inv_lst) > 1:
                inv_lst = inv_lst[-1]
            if len(is_reconcile_invoice) > 0:
                inv_lst = list(set(is_reconcile_invoice))
            for invoice in inv_obj.browse(self._cr, SUPERUSER_ID, inv_lst):
                for inv in invoice.invoice_line:
                    a = {
                        'inv': invoice.number,
                        'name': inv.name,
                        'price': round(inv.price_subtotal, prec),
                        'balance': invoice.residual,
                    }
                    invoice_details_list.append(a)
            return invoice_details_list
    #
    # def get_address(self):
    #     a = self.partner_id
    #     s1= ""
    #     s2 =""
    #     s3= ""
    #     s4 = ""
    #     s5 = ""
    #     s6 = ""
    #     if a.street:
    #         s1 = str(a.street)
    #     if a.street2:
    #         s2 = str(a.street2)
    #     if a.city:
    #         s3 = str(a.city)
    #     if a.state_id.name:
    #         s4 = str(a.state_id.name)
    #     if a.country_id.name:
    #         s5 = str(a.country_id.name)
    #     if a.zip:
    #         s6 = str(a.zip)
    #     a1 = {
    #         'street': s1,
    #         'street2': s2,
    #         'city': s3,
    #         'state_id': s4,
    #         'zip': s6,
    #         'country_id': s5,
    #     }

    def get_balance(self):
        balance = 0
        if self.ids:
            data = self.ids
            inv_lst = []
            inv_obj = self.pool.get('account.invoice')
            voucher_obj = self.pool.get('account.voucher')
            obj_precision = self.pool.get('decimal.precision')
            prec = obj_precision.precision_get(self._cr, SUPERUSER_ID, 'Account')
            cr_ln = voucher_obj.browse(self._cr, SUPERUSER_ID, self._ids).line_cr_ids
            is_reconcile = []
            if len(cr_ln) == 1:
                for cr1 in cr_ln:
                    if cr1.move_line_id and cr1.move_line_id.invoice:
                        if cr1.reconcile == True:
                            is_reconcile.append(cr1.move_line_id.invoice.id)
                        inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile.append(cr1.move_line_id.invoice.id)
            else:
                for cr1 in cr_ln:
                    if cr1.reconcile == True:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            inv_lst.append(cr1.move_line_id.invoice.id)
                            is_reconcile.append(cr1.move_line_id.invoice.id)
                    else:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile.append(cr1.move_line_id.invoice.id)

            if len(inv_lst) > 1:
                inv_lst = inv_lst[-1]
            if len(is_reconcile) > 0:
                inv_lst = list(set(is_reconcile))
            for invoice in inv_obj.browse(self._cr, SUPERUSER_ID, inv_lst):
                balance = balance + round(invoice.residual, prec),
            if balance:
                balance = balance[0]
            return balance

    def get_paid(self):
        balance = 0
        if self.ids:
            data = self.ids
            inv_lst = []
            inv_obj = self.pool.get('account.invoice')
            voucher_obj = self.pool.get('account.voucher')
            obj_precision = self.pool.get('decimal.precision')
            prec = obj_precision.precision_get(self._cr, SUPERUSER_ID, 'Account')
            cr_ln = voucher_obj.browse(self._cr, SUPERUSER_ID, self._ids).line_cr_ids
            is_reconcile = []
            if len(cr_ln) == 1:
                for cr1 in cr_ln:
                    if cr1.move_line_id and cr1.move_line_id.invoice:
                        if cr1.reconcile == True:
                            is_reconcile.append(cr1.move_line_id.invoice.id)
                        inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile.append(cr1.move_line_id.invoice.id)
            else:
                for cr1 in cr_ln:
                    if cr1.reconcile == True:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            is_reconcile.append(cr1.move_line_id.invoice.id)
                            inv_lst.append(cr1.move_line_id.invoice.id)
                    else:
                        if cr1.move_line_id and cr1.move_line_id.invoice:
                            inv_lst.append(cr1.move_line_id.invoice.id)
                    if cr1.amount > 0:
                        is_reconcile.append(cr1.move_line_id.invoice.id)
            if len(inv_lst) > 1:
                inv_lst = inv_lst[-1]
            if len(is_reconcile) > 0:
                inv_lst = list(set(is_reconcile))
            for invoice in inv_obj.browse(self._cr, SUPERUSER_ID, inv_lst):
                balance = balance + round(invoice.amount_total - invoice.residual, prec)
            return balance

            #     def _compute_inv(self):
            #         mv = self.move_id
            #         invs = self.env['account.invoice'].search([('move_id', '=', mv.id)], limit=1)
            #         self.inv_ids = invs
            #
            #     inv_ids = fields.Many2many('account.invoice', string='Payments',
            #         compute='_compute_inv')

    @api.multi
    def receipt_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'openeducat_ext.report_receipt')