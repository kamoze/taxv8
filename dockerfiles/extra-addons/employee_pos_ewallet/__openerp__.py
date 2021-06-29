{
	'name' : 'Employee Ewallet',  
	'version' : '1.0',
	'author' : 'SpantreeNG',
	'category' : 'Generic Modules/Medical',
	'depends' : [ 'hr','hr_payroll', 'account','mrp','point_of_sale','base',],
	'summary' : 'Complete Hospital Information System',
	'description' : """



""",
	"website" : "http://www.spantreeng.com",
	"init" : [],

	"data" : [ 'deposite_management/security/security.xml',
               "deposite_management/security/ir.model.access.csv",
             #  'security/application_security.xml',
           # 'security/ir.model.access.csv',
             "deposite_management/report/report_receipt.xml",
             "deposite_management/data/templates.xml",
             "deposite_management/employee/employee_view.xml",
              "deposite_management/employee/employee_report_wiz.xml",
              "deposite_management/view/employee_expense_deposite_template.xml",
              'deposite_management/employee/employee_fund_transfer_view.xml',
              'deposite_management/employee/emp_pay_in_wiz_view.xml',
              'deposite_management/employee/emp_pay_out_view.xml',
              'deposite_management/employee/reconcile_overspend_view.xml',
              'deposite_management/employee/reconcilation_credit_amount.xml',
              'geo_cafeteria/views/mrp_view.xml',
               'pos_self_service/security/application_security.xml',
              'pos_self_service/base/wizard/wizard_deposit_view.xml',
              'pos_self_service/base/base_view.xml',
              'pos_self_service/point_of_sale/point_of_sale_view.xml',
              'pos_self_service/views/pos_self_service.xml',
              'pos_self_service/wizard/shop_report_wiz_view.xml',
              'pos_self_service/wizard/pos_self_service_wiz_view.xml',
              'pos_self_service/report/template_shop_report.xml',
              'pos_self_service/report/report.xml',
              'pos_self_service/report/expanded_orders_report_view.xml',
              'pos_self_service/wizard/pos_order_confirm_wiz_view.xml',

			],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/backend.xml',
    ],
	"active": False 
}
