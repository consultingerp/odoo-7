# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GhuAdvisor(models.Model):
    _name = 'ghu.advisor'
    _description = "Advisor"

    _inherits = {"res.partner": "partner_id"}

    advisor_id = fields.Char('Advisor ID', size=12)

    last_name = fields.Char('Last Name', size=128)

    nomination = fields.Char('Nomination', size=128)

    academic_degree = fields.Char('Academic Degree', size=128)

    skype = fields.Char('Skype', size=128)

    nationality = fields.Many2one(
        string=u'Nationality',
        comodel_name='res.country'
    )
        
    native_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='res.lang'
    )

    foreign_languages = fields.Many2many(
        string=u'Foreign Languages',
        comodel_name='res.lang',
        relation='advisor_lang_rel',
        column1='advisor_id',
        column2='lang_id'
    )
    
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
        string='Gender',
        required=True)
        
    birth_date = fields.Date(
        string=u'Birthday',
        default=fields.Date.context_today
    )

    vita = fields.Binary('Vita')

    programs = fields.Many2many(
        string=u'Programs',
        comodel_name='ghu.program',
        relation='advisor_program_rel',
        column1='advisor_id',
        column2='program_id',
    )