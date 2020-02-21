{
    # Theme information
    'name': "Theme Campus",
    'description': """
    """,
    'category': 'Theme',
    'version': '1.06',
    'depends': ['website','website_theme_install'],

    # templates
    'data': [
        #'views/options.xml',
        #'views/snippets.xml',
        'views/common/layout.xml',
        'views/common/assets.xml',
        #'views/common/header.xml',
        'views/navigation/navbars.xml',
        'views/navigation/sidebars/account.xml',
        'views/navigation/sidebars/custom_mba.xml',
        'views/navigation/sidebars/advisor.xml',
        'views/navigation/sidebars/student.xml',
        'views/navigation/sidebars/doctoral_advisor.xml',
        'views/navigation/sidebars/doctoral_student.xml'
    ],

    # demo pages
    'demo': [
        'demo/pages.xml',
    ],

    # Your information
    'author': "My Company",
    'website': "",
}