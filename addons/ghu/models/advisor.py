# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GhuAdvisor(models.Model):
    _name = 'ghu.advisor'
    _description = "Advisor"
    _order = "nomination DESC, nationality ASC, lastname ASC"
    _inherit = ['website.published.mixin', 'mail.thread']
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")

    is_cafeteria = fields.Boolean(
        string=u'Is Custom MBA?',
    )
    
    is_bsc_ba = fields.Boolean(
        string=u'Is BSc?',
    )
    
    is_msc_ba = fields.Boolean(
        string=u'Is MSc?',
    )

    is_advisor = fields.Boolean(
        string=u'Is Phd/DBA advisor?',
    )

    advisor_id = fields.Char('Advisor ID', size=12)

    nomination = fields.Char('Nomination', size=128)

    academic_degree = fields.Char('Academic Degree', size=128)

    skype = fields.Char('Skype', size=128)

    nationality = fields.Many2one(
        string=u'Nationality',
        comodel_name='res.country'
    )

    native_language = fields.Many2one(
        string=u'Campus Language',
        comodel_name='res.lang'
    )
    
    mother_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='ghu.lang'
    )

    foreign_languages = fields.Many2many(
        string=u'Teaching Languages',
        comodel_name='ghu.lang',
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
    vita_filename = fields.Char(
        string=u'Vita Filename',
    )

    degree = fields.Binary(
        string='Degree GHU'
    )
    degree_filename = fields.Char(
        string=u'Degree Filename',
    )

    certificate_file = fields.Binary('Certificate PDF')
    certificate_file_filename = fields.Char(
        string=u'Certificate Filename',
    )

    certificate_original_file = fields.Binary('Certificate Word')
    certificate_original_file_filename = fields.Char(
        string=u'Certificate Filename Word',
    )

    agreement = fields.Binary(
        string=u'Doctoral Program Agreement',
    )
    agreement_filename = fields.Char(
        string=u'Doctoral Program Agreement Filename',
    )

    cmba_agreement = fields.Binary(
        string=u'Custom MBA Agreement',
    )
    cmba_agreement_filename = fields.Char(
        string=u'Custom MBA Agreement Filename',
    )
    
    
    msc_agreement = fields.Binary(
        string=u'MSc Agreement',
    )
    msc_agreement_filename = fields.Char(
        string=u'MSc Agreement Filename',
    )
    
    
    bsc_agreement = fields.Binary(
        string=u'BSc Agreement',
    )
    bsc_agreement_filename = fields.Char(
        string=u'BSc Agreement Filename',
    )

    programs = fields.Many2many(
        string=u'Programs',
        comodel_name='ghu.program',
        relation='advisor_program_rel',
        column1='advisor_id',
        column2='program_id',
    )

    pts = fields.Integer(
        string=u'PTS',
        help=u'Publication Total Score'
    )

    pts_p = fields.Integer(
        string=u'PTS-P',
        help=u'Publication Score Professional'
    )

    pts_r = fields.Integer(
        string=u'PTS-R',
        help=u'Publication Score Academic/Research'
    )

    pes = fields.Integer(
        string=u'PES',
        help=u'Professional Experience Score'
    )

    tes = fields.Integer(
        string=u'TES',
        help=u'Teaching Experience Score'
    )

    ets = fields.Integer(
        string=u'Total Score',
        help=u'Evaluation Total Score'
    )

    @api.multi
    def all_languages(self):
        res = set()
        for advisor in self:
            res.update(advisor.foreign_languages)

        return sorted(res, key=lambda lang: lang.name.lower() if lang.name else "")

    @api.multi
    def all_countries(self):
        res = set()
        for advisor in self:
            res.add(advisor.nationality)

        return sorted(res, key=lambda nationality: nationality.name.lower() if nationality.name else "")

    @api.multi
    def all_programs(self):
        res = set()
        for advisor in self:
            res.update(advisor.programs)

        return sorted(res, key=lambda program: program.name.lower() if program.name else "")


class GhuLang(models.Model):
    _name = 'ghu.lang'
    _rec_name = 'name'
    _description = "Language"

    name = fields.Char('Name', size=128)
