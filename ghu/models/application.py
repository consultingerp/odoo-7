# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GhuApplication(models.Model):
    _name = 'ghu.application'
    _description = "Application"

    title = fields.Text("Title")
    first_name = fields.Text("First Name")
    last_name = fields.Text("Last Name")
    title_post = fields.Text("Title (post)")
    
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
        string='Gender',
        required=True,
        states={'done': [('readonly', True)]})
    
    marital_status = fields.Selection(
        string=u'Marital Stauts',
        selection=[('single', 'Single')]
    )
    
    birthday = fields.Date(
        string=u'Birthday',
        default=fields.Date.context_today
    )

    nationality = fields.Many2one(
        string=u'res.country',
        comodel_name='Nationality'
    )
    
    native_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='res.lang'
    )

    foreign_languages = fields.Many2many(
        string=u'Foreign Languages',
        comodel_name='res.lang',
        relation='application_lang_rel',
        column1='application_id',
        column2='lang_id'
    )

    street = fields.Char(
        'Street', size=256, states={'done': [('readonly', True)]})

    street2 = fields.Char(
        'Street2', size=256, states={'done': [('readonly', True)]})

    city = fields.Char('City', size=64, states={'done': [('readonly', True)]})

    zip = fields.Char('Zip', size=8, states={'done': [('readonly', True)]})

    state_id = fields.Many2one(
        'res.country.state', 'States', states={'done': [('readonly', True)]})

    country_id = fields.Many2one(
        'res.country', 'Country', states={'done': [('readonly', True)]})

    phone = fields.Char(
        'Phone', size=16, states={'done': [('readonly', True)],
                                  'submit': [('required', True)]})
    mobile = fields.Char(
        'Mobile', size=16,
        states={'done': [('readonly', True)], 'submit': [('required', True)]})
    email = fields.Char(
        'Email', size=256, required=True,
        states={'done': [('readonly', True)]})

    fees = fields.Float('Fees', states={'done': [('readonly', True)]})
    
    image = fields.Binary('image', states={'done': [('readonly', True)]})

    state = fields.Selection(
        [('new', 'New'),
         ('confirm', 'Confirmed'),
         ('reject', 'Rejected'),
         ('pending', 'Pending'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        'State', default='draft', track_visibility='onchange')


    student_id = fields.Many2one(
        'op.student', 'Student', states={'done': [('readonly', True)]}
    )

    product_id = fields.Many2one(
        'product.product', 'Product', required=True,
        domain=[('type', '=', 'service')], readonly=True)

    course_id = fields.Many2one(
        'ghu.course', 'Course', required=True, readonly=True)

    partner_id = fields.Many2one('res.partner', 'Partner')
    is_student = fields.Boolean('Is Already Student')
    fees_term_id = fields.Many2one('op.fees.terms', 'Fees Term')
    
class qualification(models.Model):
    _name = 'ghu.qualification'
    _description = "Qualification"
    register_id = fields.Many2one(
        'op.admission.register', 'Admission Register', required=True,
        states={'done': [('readonly', True)]})
