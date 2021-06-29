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

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.constrains('ean13')
    def _check_partner_ean_no(self):
        """
            Apply constrains for EAN13 code to accept only
            unique values
        """
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([])
        ean_list = []
        partner_ids = self.search([('id','!=', self.id)])
        ## Get EAN for Partner
        for partner_id in partner_ids:
            if partner_id.ean13:
                ean_list.append(partner_id.ean13)
        ## get EAN for Employee
        for employee_id in employee_ids:
            if employee_id.ean13:
                ean_list.append(employee_id.ean13)
        if self.ean13 in ean_list:
            raise except_orm(_('Warning!'),
                             _("A EAN Code can\'t have duplicate values."))
