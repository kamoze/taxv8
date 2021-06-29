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

import datetime
import calendar
import time
from openerp.osv import osv, fields
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp import netsvc


class student_deposite_expense_wiz_report(report_sxw.rml_parse):
    _name = "report.deposite_management.student_deposite_expense_wiz_report"
    total_balance, total_deposit_to_amount, total_credit, total_expense = 0.0, 0.0, 0.0, 0.0
    
    def __init__(self, cr, uid, name, context):
        super(student_deposite_expense_wiz_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_student': self.get_student,
            #'get_employee': self.get_employee,
            "get_total": self.get_total,
        })


    def get_student(self, stud, obj):
        uid, cr = 1, self.cr
        deposit_obj = self.pool.get("student.deposits")
        expense_obj = self.pool.get("student.expenses")
        deposit_ids = deposit_obj.search(cr, uid, [('name','=',stud.id), ('date','>=',obj.name), ('date','<=',obj.from_date)], order="date")
        expense_ids = expense_obj.search(cr, uid, [('name','=',stud.id), ('date','>=',obj.name), ('date','<=',obj.from_date)], order="date")

        deposit_obj_ids = deposit_obj.browse(cr, uid, deposit_ids)
        expense_obj_ids = expense_obj.browse(cr, uid, expense_ids)

        #Find all unique years on deposit and expense profile.
        deposit_years, expense_years = [], []
        for deposit in deposit_obj_ids:
            yr = None
            if deposit.date:
                date_object = datetime.datetime.strptime(deposit.date, '%Y-%m-%d %H:%M:%S')
                yr = date_object.year
            if not yr in deposit_years:
                deposit_years.append(yr)
        for expense in expense_obj_ids:
            yr = None
            if expense.date:
                date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                yr = date_object.year
            if not yr in expense_years:
                expense_years.append(yr)

        # All deposits merge into year wise with expenses.
        main_list = []
        for yr in deposit_years:
            amount_to_deposit, credit_amount, total_expense = 0.0, 0.0, 0.0
            for deposit in deposit_obj_ids:
                date_object = datetime.datetime.strptime(deposit.date, '%Y-%m-%d %H:%M:%S')
                dyr = date_object.year
                if yr == dyr:
                    amount_to_deposit += deposit.amount
                    credit_amount += deposit.paid_amount
            for expense in expense_obj_ids:
                date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                eyr = date_object.year
                if yr == eyr:
                    total_expense += expense.amount
            main_list.append([yr, str(total_expense), str(credit_amount), str(amount_to_deposit), str(credit_amount - total_expense)])

        # Only for expenses
        remain_expense_years = []
        if expense_years:
            for expense in expense_years:
                if expense not in deposit_years:
                    remain_expense_years.append(expense)

        if remain_expense_years:
            amount_to_deposit, credit_amount, total_expense = 0.0, 0.0, 0.0
            for rexpense in remain_expense_years:
                is_found = False
                for expense in expense_obj_ids:
                    date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                    eyr = date_object.year
                    if rexpense == eyr:
                        total_expense += expense.amount
                        is_found = True
                if is_found:
                    main_list.append([rexpense, str(total_expense), str(credit_amount), str(amount_to_deposit), str(credit_amount - total_expense)])
        if main_list:
            for line in main_list:
                self.total_balance += float(line[4])
                self.total_deposit_to_amount += float(line[3])
                self.total_credit += float(line[2])
                self.total_expense += float(line[1])
        return main_list

    def get_total(self):
        return [self.total_balance, self.total_deposit_to_amount, self.total_credit, self.total_expense]

    def get_employee(self, stud, obj):
        uid, cr = 1, self.cr
        deposit_obj = self.pool.get("employee.deposits")
        expense_obj = self.pool.get("employee.expenses")
        deposit_ids = deposit_obj.search(cr, uid, [('name','=',stud.id), ('date','>=',obj.name), ('date','<=',obj.from_date)], order="date")
        expense_ids = expense_obj.search(cr, uid, [('name','=',stud.id), ('date','>=',obj.name), ('date','<=',obj.from_date)], order="date")

        deposit_obj_ids = deposit_obj.browse(cr, uid, deposit_ids)
        expense_obj_ids = expense_obj.browse(cr, uid, expense_ids)

        #Find all unique years on deposit and expense profile.
        deposit_years, expense_years = [], []
        for deposit in deposit_obj_ids:
            yr = None
            if deposit.date:
                date_object = datetime.datetime.strptime(deposit.date, '%Y-%m-%d %H:%M:%S')
                yr = date_object.year
            if not yr in deposit_years:
                deposit_years.append(yr)
        for expense in expense_obj_ids:
            yr = None
            if expense.date:
                date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                yr = date_object.year
            if not yr in expense_years:
                expense_years.append(yr)

        # All deposits merge into year wise with expenses.
        main_list = []
        for yr in deposit_years:
            amount_to_deposit, credit_amount, total_expense = 0.0, 0.0, 0.0
            for deposit in deposit_obj_ids:
                date_object = datetime.datetime.strptime(deposit.date, '%Y-%m-%d %H:%M:%S')
                dyr = date_object.year
                if yr == dyr:
                    amount_to_deposit += deposit.amount
                    credit_amount += deposit.paid_amount
            for expense in expense_obj_ids:
                date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                eyr = date_object.year
                if yr == eyr:
                    total_expense += expense.amount
            main_list.append([yr, str(total_expense), str(credit_amount), str(amount_to_deposit), str(credit_amount - total_expense)])

        # Only for expenses
        remain_expense_years = []
        if expense_years:
            for expense in expense_years:
                if expense not in deposit_years:
                    remain_expense_years.append(expense)

        if remain_expense_years:
            amount_to_deposit, credit_amount, total_expense = 0.0, 0.0, 0.0
            for rexpense in remain_expense_years:
                is_found = False
                for expense in expense_obj_ids:
                    date_object = datetime.datetime.strptime(expense.date, '%Y-%m-%d %H:%M:%S')
                    eyr = date_object.year
                    if rexpense == eyr:
                        total_expense += expense.amount
                        is_found = True
                if is_found:
                    main_list.append([rexpense, str(total_expense), str(credit_amount), str(amount_to_deposit), str(credit_amount - total_expense)])
        if main_list:
            for line in main_list:
                self.total_balance += float(line[4])
                self.total_deposit_to_amount += float(line[3])
                self.total_credit += float(line[2])
                self.total_expense += float(line[1])
        return main_list


class report_student_expense_deposit_document(osv.AbstractModel):
    _name = 'report.deposite_management.report_student_expense_deposit_document'
    _inherit = 'report.abstract_report'
    _template = 'deposite_management.report_student_expense_deposit_document'
    _wrapped_report_class = student_deposite_expense_wiz_report


class report_employee_expense_deposit_document(osv.AbstractModel):
    _name = 'report.deposite_management.report_employee_expense_deposit_document'
    _inherit = 'report.abstract_report'
    _template = 'deposite_management.report_employee_expense_deposit_document'
    _wrapped_report_class = student_deposite_expense_wiz_report

