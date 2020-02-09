# -*- coding: utf-8 -*-
{
    'name': "Payment Acquirer CXPay",

    'summary': """
        Extends Authorize.net to support cxpay""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gerald Aistleitner & Robert Aistleitner",
    'website': "https://www.linkedin.com/in/gerald-aistleitner-1a2712120/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

 

    # any module necessary for this one to work correctly
    'depends': ['payment_authorize'],
    'installable': True,
}
