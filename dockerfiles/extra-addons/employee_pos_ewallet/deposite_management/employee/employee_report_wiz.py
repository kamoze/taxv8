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
import datetime
import calendar
import time
from openerp.osv import osv, fields
from openerp.tools.translate import _


class employee_deposite_expense_wiz(osv.osv_memory):
    _name = "employee.deposite.expense.wiz"
    
    _columns={
          "name": fields.date("Start Date"),
          "from_date": fields.date("End Date"),
          "employee_ids": fields.many2many("hr.employee","emp_dep_exp_wiz_report_rel","wiz_id", "emp_id", "Employees"),
      }
  
    def act_print(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        if obj.name >= obj.from_date:
            raise osv.except_osv(_('Configuration Issue!'),_("Start date should be smaller than End date!"))
        return self.pool['report'].get_action(cr, uid, [], 'employee_pos_ewallet.report_employee_expense_deposit_document', data=None, context=context)





