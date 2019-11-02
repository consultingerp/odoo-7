# -*- coding: utf-8 -*-
{
    'name': "GHU Custom MBA",

    'summary': """
        GHU's Custom MBA module""",

    'description': """
        This extension is used to offer advisors the possibility to create courses and students to study them.
    """,

    'author': "Gerald Aistleitner & Robert Aistleitner",
    'website': "https://www.linkedin.com/in/gerald-aistleitner-1a2712120/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',

    'version': '0.48',


    # any module necessary for this one to work correctly
    'depends': ['ghu', 'documents'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/scheduled_actions.xml',
        'views/views.xml',
        'views/application/form.xml',
        'views/course/advisor/list.xml',
        'views/course/advisor/detail.xml',
        'views/course/advisor/edit.xml',
        'views/course/advisor/record.xml',
        'views/course/advisor/assessments/edit.xml',
        'views/course/advisor/assessments/question/edit.xml',
        'views/course/student/overview.xml',
        'views/course/student/preview.xml',
        'views/video/myvideos.xml',
        'views/video/panopto.xml',
        'views/documents/list.xml',
        'views/common/layout.xml',
        'views/common/vue_assets.xml',
        'views/common/intro_assets.xml',
        'views/common/panopto_login.xml',
        'views/config/res_config_settings.xml',
        'views/mails/student/inscription-approved.xml',
        'views/mails/student/inscription-received.xml',
        'views/mails/student/student-enrolled.xml',
        'views/mails/workflow/review-needed.xml',
        'views/mails/workflow/recording-review-needed.xml',
        'views/mails/workflow/script-approved.xml',
        'views/mails/workflow/correction-needed.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
    'application': True
}
