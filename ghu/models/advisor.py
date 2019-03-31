# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GhuAdvisor(models.Model):
    _name = 'ghu.advisor'
    _description = "Advisor"

    _inherits = {"res.partner": "partner_id"}

    advisor_id = fields.Char('Last Name', size=12)

    last_name = fields.Char('Last Name', size=128)
    
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
        relation='application_lang_rel',
        column1='application_id',
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

    _sql_constraints = [
        ('unique_advisor_code',
         'unique(code)', 'Code should be unique per advisor!')]