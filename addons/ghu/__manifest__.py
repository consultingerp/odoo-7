# -*- coding: utf-8 -*-
{
    'name': "GHU",

    'summary': """
        Greatest Odoo Module Ever""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gerald Aistleitner & Robert Aistleitner",
    'website': "https://www.linkedin.com/in/gerald-aistleitner-1a2712120/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.634',
 

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_automation', 'web', 'crm', 'account', 'website', 'website_form', 'website_partner', 'website_form_editor', 'hr', 'sign', 'mass_mailing','theme_treehouse', 'ghu_campus_style', 'account_transferwise'],

    # always loaded
    'data': [
        'data/application.xml',
        'data/ghu_data.xml',
        'data/website_ghu_data.xml',
        'security/ir.model.access.csv',
        'security/advisor_security.xml',
        'views/assets.xml',
        'views/advisor_view.xml',
        'views/program_view.xml',
        'views/lang_view.xml',
        'views/study_view.xml',
        'views/employee_view.xml',
        'views/footer_view.xml',
        'views/email_signature_view.xml',
        'views/lead_view.xml',
        'views/sign_view.xml',
        'views/application_view.xml',
        'views/application_pdf.xml',
        'views/application_report.xml',
        'views/report_style.xml',
        'views/newsletter_footer_view.xml',
        'views/web_style.xml',
        'views/student/enrolment_confirmation_pdf.xml',
        'menu/ghu_menu.xml',
        'menu/advisor_menu.xml',
        'views/application_form.xml',
        'views/res_config_view.xml',
        'views/invoice_document.xml',
        'views/website_social_header.xml',
        'views/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True
}
