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
import urllib
import urllib2
from openerp.exceptions import except_orm, Warning, RedirectWarning
from lxml import etree
from openerp.osv.orm import setup_modifiers

import logging
_logger = logging.getLogger(__name__)


class op_student(models.Model):
    _inherit = "op.student"

    @api.constrains('pin')
    def pin_range(self):
        for each in self:
            if each.pin:
                if len(each.pin) < 4:
                    raise except_orm(_('Warning'),
                                _("Please enter 4 digit pin only."))

    pin = fields.Char('PIN')

    @api.model
    def is_account_officer(self):
        ''' Function to check user if it is  Account Officer'''
        group_id = self.env['ir.model.data'].get_object_reference(
            'account', 'group_account_user')
        group_id = group_id and group_id[1] or False
        group_rec = self.env['res.groups'].browse(group_id)
        group_user_ids = [x.id for x in group_rec.users]
        if self._uid in group_user_ids:
            return True
        else:
            return False

    @api.model
    def is_account_manager(self):
        ''' Function to check user if it is  Account Manager'''
        group_id = self.env['ir.model.data'].get_object_reference(
            'account', 'group_account_manager')
        group_id = group_id and group_id[1] or False
        group_rec = self.env['res.groups'].browse(group_id)
        group_user_ids = [x.id for x in group_rec.users]
        if self._uid in group_user_ids:
            return True
        else:
            return False

    @api.model
    def fields_view_get(self, view_id=None,
                        view_type='form', context=None,
                        toolbar=False, submenu=False):
        context = context or {}
        res = super(op_student, self). \
            fields_view_get(
            view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == "form":
            if not self.is_account_officer() or not self.is_account_manager():
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='ean13']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, res['fields']['ean13'])
                res['arch'] = etree.tostring(doc)
        return res


class hr_employee(models.Model):
    _inherit = "hr.employee"

    @api.constrains('pin')
    def pin_range(self):
        for each in self:
            if each.pin:
                if len(each.pin) < 4 or len(each.pin) > 4:
                    raise except_orm(_('Warning'),
                                _("Please enter 4 digit pin only."))

    pin = fields.Char('PIN')
    ean13 = fields.Char('EAN13')

    @api.model
    def is_account_officer(self):
        ''' Function to check user if it is  Account Officer'''
        group_id = self.env['ir.model.data'].get_object_reference(
            'account', 'group_account_user')
        group_id = group_id and group_id[1] or False
        group_rec = self.env['res.groups'].browse(group_id)
        group_user_ids = [x.id for x in group_rec.users]
        if self._uid in group_user_ids:
            return True
        else:
            return False

    @api.model
    def is_account_manager(self):
        ''' Function to check user if it is  Account Manager'''
        group_id = self.env['ir.model.data'].get_object_reference(
            'account', 'group_account_manager')
        group_id = group_id and group_id[1] or False
        group_rec = self.env['res.groups'].browse(group_id)
        group_user_ids = [x.id for x in group_rec.users]
        if self._uid in group_user_ids:
            return True
        else:
            return False

    @api.model
    def fields_view_get(self, view_id=None,
                        view_type='form', context=None,
                        toolbar=False, submenu=False):
        context = context or {}
        res = super(hr_employee, self). \
            fields_view_get(
            view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu)

        if view_type == "form":
            if not self.is_account_officer() or not self.is_account_manager():
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='ean13']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, res['fields']['ean13'])
                res['arch'] = etree.tostring(doc)
        return res
