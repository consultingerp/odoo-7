# -*- coding: utf-8 -*-
{
    'name': "account_transferwise",

    'summary': """
        Use Transferwise.com to retrieve bank statements""",

    'description': """
        Use Transferwise.com to retrieve bank statements.
    """,

    'category': 'Accounting',
    'version': '3.0',

    'depends': ['account_online_sync'],

    'data': [
        'views/transferwise_views.xml',
    ],
    'license': 'OEEL-1',
    'auto_install': True,
}
