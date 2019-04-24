# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GhuApplication(models.Model):
    _name = 'ghu.application'
    _description = 'GHU Application'

    # PERSONAL DATA FIELDS
    first_name = fields.Char(
        'First Name', 
        size=256, 
        required=True
    )
    last_name = fields.Char(
        'Last Name', 
        size=256, 
        required=True
    )
    date_of_birth = fields.Date(
        string=u'Date of Birth',
        required=True,
    )
    nationality = fields.Many2one(
        string=u'Nationality',
        comodel_name='res.country',
        required=True,
    )
    marital_status = fields.Selection(
        string=u'Marital Status',
        selection=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('separated', 'Separated'),
            ('widowed', 'Widowed'),
        ]
    )
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
        string='Gender',
        required=True,
        states={'done': [('readonly', True)]}
    )
    academic_degree_pre = fields.Char(
        'Academic Degrees (Pre)', 
        size=64,
    )
    academic_degree_post = fields.Char(
        'Academic Degrees (Post)', 
        size=64,
    )
    native_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='ghu.lang',
        required=True,
    )
    other_languages = fields.Many2many(
        string=u'Other Languages',
        comodel_name='ghu.lang',
        relation='ghu_application_lang_rel',
        column1='application_id',
        column2='lang_id'
    )

    # RESIDENTIAL ADDRESS FIELDS
    street = fields.Char(
        'Street', 
        size=256, 
        required=True, 
        states={'done': [('readonly', True)]}
    )
    zip = fields.Char('Zip', size=16, states={'done': [('readonly', True)]})
    city = fields.Char('City', size=128, states={'done': [('readonly', True)]})

    country_id = fields.Many2one(
        'res.country', 'Country', states={'done': [('readonly', True)]})
    phone = fields.Char(
        'Phone', size=64, states={'done': [('readonly', True)]}
    )
    email = fields.Char(
        'Email', size=256, required=True,
        states={'done': [('readonly', True)]}
    )


    # STUDY PROGRAM FIELDS
    study_id = fields.Many2one(
        'ghu.study', 'Study', required=True
    )

    preliminary_studies = fields.One2many(
        'ghu.application_study',
        'application_id',
        string='Preliminary Studies',
    )
    ever_applied_at_ghu = fields.Boolean(
        'Ever applied to GHU',
        required=True,
    )
    ever_applied_doctoral = fields.Boolean(
        'Has ever applied for a doctoral degree',
        required=True,
    )
    ever_applied_doctoral_university_name = fields.Char(
        'University name where applied for doctoral degree',
        size=256,
        required=False,
    )

    # REQUIRED DOCUMENTS
    photo_file = fields.Binary('Photo', required=True)
    vita_file = fields.Binary('Curriculum Vitae', required=True)
    passport_file = fields.Binary('Copy of Passport', required=True)
    degrees_file = fields.Binary('Copies of degrees', required=True)
    research_abstract_file = fields.Binary('Title and Abstract of intended research', required=True)

    # PAYMENT FIELDS
    payment_method = fields.Selection(
        string=u'Payment Method',
        selection=[
            ('one_time', 'One-time payment'),
            ('two_times', 'Two-time payment'),
            ('three_times', 'Three-time payment'),
        ]
    )
    payment_full_name = fields.Char('Payment Full Name', size=256, required=True)
    payment_street = fields.Char('Payment Street', size=256, required=True)
    payment_zip = fields.Char('Payment Zip', size=16, required=True)
    payment_city = fields.Char('Payment City', size=128, required=True)
    payment_country = fields.Many2one(
        'res.country', 'Payment Country', required=True)
    payment_phone = fields.Char('Payment Phone', size=64, required=True)
    payment_email = fields.Char('Payment Email', size=256, required=True)


    # PROCESS FIELDS
    state = fields.Selection(
        [
            ('new', 'New'),
            ('confirm', 'Confirmed'),
            ('reject', 'Rejected'),
            ('pending', 'Pending'),
            ('cancel', 'Cancelled'),
            ('done', 'Done')
        ],
        'State', default='new', required=True, track_visibility='onchange'
    )

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        states={'done': [('readonly', True)]},
    )

    product_id = fields.Many2one(
        'product.product',
        'Product',
        domain=[('type', '=', 'service')],
    )


class GhuApplicationStudy(models.Model):
    _name = 'ghu.application_study'
    _description = 'GHU Application Preliminary Studies'
    _log_access = False

    institution = fields.Char('Institution', size=256, required=True)
    city = fields.Char('City', size=128, required=True)
    from_date = fields.Date(
        string=u'From',
        required=True,
    )
    to_date = fields.Date(
        string=u'To',
        required=True,
    )
    subject = fields.Char('Subject', size=256, required=True)
    diploma = fields.Char('Diploma', size=256, required=True)
    credit_points = fields.Integer('Credit Points', required=True)

    application_id = fields.Many2one(
        'ghu.application',
        string='GHU Application',
    )
