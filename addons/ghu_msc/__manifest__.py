# -*- coding: utf-8 -*-
{
    'name': "GHU MSc program",

    'summary': """
        This module is used to manage master programs.""",


    'author': "Gerald Aistleitner",
    'website': "http://www.ghu.edu.cw",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.120',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'ghu', 'ghu_custom_mba'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/activity_types.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/application/form.xml',
        'views/application/backend_application_views.xml',
        'views/mails/application/application_received.xml',
        'views/mails/application/portal_access.xml',
        'views/study/backend.xml',
        'security/ir.model.access.csv'
    ],
}
