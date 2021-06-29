{
    'name' : 'Application',
    'version' : '1.0',
    'author' : 'SpantreeNG',
    'category' : 'E-Tax Application',
    'description': """

    """,
    'website': 'http://www.spantreeng.com',
    'images' : [],
    'depends' : ['auth_signup','etax','base','product','account', 'account_voucher', 'stock', 'hr','analytic'],
    'data': [
        "security/application_security.xml",
        "security/ir.model.access.csv",
        "application_view.xml",
        "sequence.xml",
        "sign_up.xml",
        'report_receipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}
