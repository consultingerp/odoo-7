# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ghu_msc_application(models.Model):
    _name = 'ghu_msc.application'
    _rec_name = 'lastname'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MSc Application'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        required=True,
        states={'done': [('readonly', True)]},
    )

    firstname = fields.Char(related='partner_id.firstname', required=True)
    lastname = fields.Char(related='partner_id.lastname', required=True)

    gender = fields.Selection(related='partner_id.gender', required=True)

    nationality = fields.Many2one('res.country', 'Nationality', required=True,
                                  states={'finished': [('readonly', True)]})
    date_of_birth = fields.Date(
        string=u'Date of Birth',
        required=True,
        states={'finished': [('readonly', True)]}
    )

    academic_degree_pre = fields.Char(
        'Academic Degrees (Pre)',
        size=64,
        states={'finished': [('readonly', True)]}
    )
    academic_degree_post = fields.Char(
        'Academic Degrees (Post)',
        size=64,
        states={'finished': [('readonly', True)]}
    )
    native_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='ghu.lang',
        required=True,
        states={'finished': [('readonly', True)]}
    )
    other_languages = fields.Many2many(
        string=u'Other Languages',
        comodel_name='ghu.lang',
        relation='ghu_msc_application_lang_rel',
        column1='application_id',
        column2='lang_id',
        states={'finished': [('readonly', True)]}
    )

    vita_file = fields.Binary('Curriculum Vitae', required=True, states={'finished': [('readonly', True)]})
    vita_file_filename = fields.Char(
        string=u'vita_filename',
        states={'finished': [('readonly', True)]}
    )

    id_file = fields.Binary('Personal ID (Passport, Driver License,...)', required=True, states={'finished': [('readonly', True)]})
    id_file_filename = fields.Char(
        string=u'id_filename',
        states={'finished': [('readonly', True)]}
    )

    email = fields.Char(related='partner_id.email', required=True)

    # STUDY PROGRAM FIELDS
    study_id = fields.Many2one(
        'ghu.study', 'Study', domain=[('code', 'ilike', 'MSC')], required=True,
        states={'finished': [('readonly', True)]}
    )

    states = [
        ('new', 'New (Please review application)'),
        ('needs_sync', 'Sync needed (Talk to partner university)'),
        ('approved', 'Waiting for payment'),
        ('finished', 'Completed')
    ]

    state = fields.Selection(
        states,
        'State', default='new', required=True, track_visibility='onchange', group_expand='_read_group_stage_ids'
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return [k for k, v in self.states]

    @api.multi
    def write(self, values):
        if 'state' in values:
            self.on_state_change(values['state'])
        super(ghu_msc_application, self).write(values)

    def on_state_change(self, new_state):
        # generate invoice
        self_sudo = self.sudo()
        if new_state == 'needs_sync':
            print('Application needs sync with other university.')
            # self_sudo.send_application_fee_invoice()
        elif new_state == 'approved':
            self_sudo.send_invoice()
        elif new_state == 'finished':
            self_sudo.end_application()

    @api.multi
    def application_received(self):
        print('Post message: Received application')
        # TODO: Post Message to Thread
        notification_template_en = self.env.ref(
            'ghu_msc.application_received_en').sudo()
        notification_template_es = self.env.ref(
            'ghu_msc.application_received_es').sudo()
        for record in self:
            if record.native_language.name == 'Spanish':
                record.message_post_with_template(template_id=notification_template_es.id)
            else:
                record.message_post_with_template(template_id=notification_template_en.id)
        return True

    @api.multi
    def approve_application(self):
        for record in self:
            if record.study_id.partner_university_id:
                record.write({'state': 'needs_sync'})
            else:
                record.write({'state': 'approved'})

    @api.multi
    def application_approved_by_partner(self):
        for record in self:
            record.write({'state': 'approved'})

    @api.multi
    def send_invoice(self):
        for record in self:
            print('Application approved')
            # TODO: Send invoice for selected study

    @api.multi
    def end_application(self):
        for record in self:
            print('Student enrolled')
            # TODO: Enroll student
