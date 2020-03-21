# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from odoo.tools import email_split


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


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

    program_fee_invoice_id = fields.Many2one(
        'account.invoice',
        'Program Fee Invoice',
    )

    id_file = fields.Binary('Personal ID (Passport, Driver License,...)', required=True,
                            states={'finished': [('readonly', True)]})
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
        ('approved', 'Waiting for payment'),
        ('needs_sync', 'Sync needed (Talk to partner university)'),
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
        self.ensure_one()
        self_sudo = self.sudo(self.env().user)

        if new_state == 'approved':
            self_sudo.send_invoice()
        elif new_state == 'needs_sync':
            # TODO: Create campus access
            self_sudo.create_portal_access()
            template = self_sudo.env.ref('ghu_msc.portal_access')
            self_sudo.partner_id.message_post_with_template(
                template_id=template.with_context(dbname=self_sudo._cr.dbname, lang=self.partner_id.user_ids[0].lang).id)
            print('Application needs sync with other university.')
            self.env['mail.activity'].sudo().create({
                'res_model_id': self.env.ref('ghu_msc.model_ghu_msc_application').id,
                'res_id': self.id,
                'user_id': 8,
                'activity_type_id': self.env.ref('ghu_msc.ghu_activity_data_check_with_partner_university').id,
                'summary': 'Please check if partner university has student as well.',
                'date_deadline': datetime.now() + timedelta(days=7),
            })
        elif new_state == 'finished':
            if self.state == 'needs_sync':
                # TODO: Create only enrollment
                self_sudo.create_enrollment()
            elif self.state == 'approved':
                # TODO: Create campus access and enrollment
                self_sudo.create_portal_access()
                self_sudo.create_enrollment()

    @api.multi
    def application_received(self):
        print('Post message: Received application')
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
            record.write({'state': 'approved'})

    @api.multi
    def application_approved_by_partner(self):
        for record in self:
            record.write({'state': 'finished'})

    @api.multi
    def send_invoice(self):
        for record in self:
            print('Application approved')
            # get proper product
            if self.study_id.product_id:
                invoice = self.env['account.invoice'].create(dict(
                    # customer (billing address)
                    partner_id=self.partner_id.id,
                    type='out_invoice',
                    date_invoice=datetime.utcnow().date(),  # invoice date
                    user_id=2,  # salesperson Gerald
                    invoice_line_ids=[],  # invoice lines
                    name=self.study_id.name,  # name for account move lines
                    partner_bank_id=self.env['ir.config_parameter'].get_param(
                        'ghu.automated_invoice_bank_account'),  # company bank account
                ))

                invoice_line = self.env['account.invoice.line'].with_context(
                    type=invoice.type,
                    journal_id=invoice.journal_id.id,
                    default_invoice_id=invoice.id
                ).create(dict(
                    product_id=self.study_id.product_id.id,
                    name=self.study_id.product_id.name,
                    price_unit=self.study_id.product_id.lst_price,
                ))

                invoice.invoice_line_ids = [(4, invoice_line.id)]

                invoice.message_subscribe([3, 7, 11])

                self.program_fee_invoice_id = invoice.id

                self.env['mail.activity'].sudo().create({
                    'res_model_id': self.env.ref('account.model_account_invoice').id,
                    'res_id': invoice.id,
                    'user_id': 8,
                    'activity_type_id': self.env.ref('ghu_msc.ghu_activity_data_validate_invoice').id,
                    'summary': 'Please check scholarship and payment terms with applicant and then validate and send invoice.',
                    'date_deadline': datetime.now() + timedelta(days=3),
                })
                # TODO: Send invoice for selected study

    @api.multi
    def invoice_paid(self):
        for record in self:
            print('Application approved')
            if record.study_id.partner_university_id:
                record.write({'state': 'needs_sync'})
            else:
                record.write({'state': 'finished'})

    @api.one
    def create_portal_access(self):
        self.ensure_one()
        self_sudo = self.sudo(self.env().user)
        # Create Portal Access for student if there is no one yet
        notification_template = self_sudo.env.ref(
            'ghu_msc.portal_access').sudo()
        user = self.partner_id.user_ids[0] if self.partner_id.user_ids else None
        if not user:
            user = self_sudo.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
                'email': extract_email(self.partner_id.email),
                'login': extract_email(self.partner_id.email),
                'partner_id': self.partner_id.id,
                'company_id': 1,
                'company_ids': [(6, 0, [1])],
            })
            partner = self.partner_id
            lang = user.lang
            return partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                partner.id]
        return False

    @api.one
    def create_enrollment(self):
        self.ensure_one()
        self_sudo = self.sudo(self.env().user)
        # Check if student exists
        student = self_sudo.env['ghu.student'].search([('partner_id.id', '=', self.partner_id.id)], limit=1)
        if not student:
            student = self_sudo.env['ghu.student'].create(dict(
                partner_id=self.partner_id.id,
                vita_file=self.vita_file,
                vita_file_filename=self.vita_file_filename,
                id_file=self.id_file,
                id_file_filename=self.id_file_filename,
                date_of_birth=self.date_of_birth,
                nationality=self.nationality.id,
                academic_degree_pre=self.academic_degree_pre,
                academic_degree_post=self.academic_degree_post,
                native_language=self.native_language.id,
                other_languages=(6, False, [v.id for v in self.other_languages])
            ))

        enrollment = self_sudo.env['ghu_msc.enrollment'].create(dict(
            student_ref='%s,%s' % ('ghu.student', student.id),
            study_ref='%s,%s' % ('ghu.study', self.study_id.id),
            invoice_ref='%s,%s' % ('account.invoice', self.program_fee_invoice_id.id)
        ))

        # TODO: Create enrollment for MSc


class ghu_msc_enrollment(models.Model):
    _name = 'ghu_msc.enrollment'
    _inherit = ['ghu.enrollment']
