# -*- coding: utf-8 -*-
{
    'name': "GHU",

    'summary': """
        Greatest Odoo Module Ever""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gerald Aistleitner",
    'website': "https://www.linkedin.com/in/gerald-aistleitner-1a2712120/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.25',
 
    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'account', 'website', 'website_form', 'website_partner', 'website_form_editor'],

    # always loaded
    'data': [
        'data/ghu_data.xml',
        'data/website_ghu_data.xml',
        'security/ir.model.access.csv',
        'security/advisor_security.xml',
        'views/advisor_view.xml',
        'views/employee_view.xml',
        #'views/templates.xml',
        'menu/advisor_menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True
}