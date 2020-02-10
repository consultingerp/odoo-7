# -*- coding: utf-8 -*-
{
    'name': "GHU Campus Theme",

    'summary': """
        GHU's Campus Theme""",

    'description': """
        This extension is used to style the campus.
    """,

    'author': "Gerald Aistleitner & Robert Aistleitner",
    'website': "https://www.linkedin.com/in/gerald-aistleitner-1a2712120/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.271',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/common/layout.xml',
        'views/common/assets.xml',
        'views/common/header.xml',
        'views/navigation/navbars.xml',
        'views/navigation/sidebars/account.xml',
        'views/navigation/sidebars/custom_mba.xml',
        'views/navigation/sidebars/advisor.xml',
        'views/navigation/sidebars/student.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
    'application': True
}
