# -*- coding: utf-8 -*-
{
    'name': "ghu_core",

    'summary': """
        This is the basic extension of odoo for GHU""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gerald Aistleitner, gerald.aistleitner@gmail.com",
    'website': "http://ghu.edu.cw",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}