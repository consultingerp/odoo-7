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
    'category': 'Theme/Creative',
    'depends': ['web','website','website_theme_install','theme_common'],
    'version': '0.265',

    # always loaded
    'data': [
        'views/assets.xml',
        'views/images_library.xml',
        'views/images_content.xml',
        'views/layout.xml',
        'views/snippets.xml',
        'views/snippets_options.xml',
        'views/customize_modal.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
    'application': True
}