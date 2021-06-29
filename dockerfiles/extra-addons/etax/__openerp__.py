{
    'name': 'e-Tax',
    'version': '1.2',
    'category': 'Taxation',
    'description': """
               This module will be used for the customer to file their Tax.  
 """,
    'author': 'SpantreeNG',
    'website': 'http://www.spantreeng.com',
    'depends': ['base','crm_helpdesk','sale','account','website','account_voucher'],
    'data': [            
        	'security/security_view.xml',
	        'security/ir.model.access.csv',
            'email_template_view.xml',
            'etax_view.xml',
            'tax_calculator_view.xml',
            'demand_notice_view.xml',
            'tax_workflow.xml',
            'tax_sequence_view.xml',
            'assesment_form_template.xml',
            'website_js.xml',
            'wizard/select_tax_form_view.xml',
            'wizard/sequence.xml',
            'wizard/tax_calculator_form_view.xml',
            'wizard/generate_invoice_view.xml',
            'inherit_menu.xml',
            'reg_payment_mail.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
