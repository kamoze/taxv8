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

import logging
import time

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class ean_wizard(osv.osv_memory):
    _inherit = 'pos.ean_wizard'

    def sanitize_ean13(self, cr, uid, ids, context):
        user_obj = self.pool.get('res.users')
        user_info = user_obj.search(cr, uid, [('id', '=', uid)])
        user_id = user_obj.browse(cr, uid, user_info)
        student_obj = self.pool.get('op.student')
        emp_obj = self.pool.get('hr.employee')
        for r in self.browse(cr, uid, ids):
            ean13 = openerp.addons.pos_self_service.point_of_sale.product.sanitize_ean13(r.ean13_pattern)
            if user_id and not user_id.company_id.ean_prefix:
                raise osv.except_osv(_('Warning!'),
                                     _("You should configure EAN Prefix from Company configuration."))
            if user_id and user_id.company_id.ean_prefix:
                ean13 = user_id.company_id.ean_prefix + ean13

            ## Search ean no already exits or not for employee and student
            employee_id = emp_obj.search(cr, SUPERUSER_ID, [('ean13', '=', ean13)])
            if employee_id:
                raise osv.except_osv(_('Warning!'),
                                     _("This Account Number Already Assinged. Please Generate Again."))

            student_id = student_obj.search(cr, SUPERUSER_ID, [('ean13', '=', ean13)])
            if student_id:
                raise osv.except_osv(_('Warning!'),
                                     _("This Account Number Already Assinged. Please Generate Again."))
            m = context.get('active_model')
            m_id = context.get('active_id')
            self.pool[m].write(cr, uid, [m_id], {'ean13': ean13})
        return {'type': 'ir.actions.act_window_close'}