# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class GhuApplication(models.Model):
    _name = 'ghu.application'
    _description = 'GHU Application'
    _rec_name = 'lastname'

    # PERSONAL DATA FIELDS
    firstname = fields.Char(related='partner_id.firstname', required=True)
    lastname = fields.Char(related='partner_id.lastname', required=True)
    nationality = fields.Many2one('res.country', 'Nationality', required=True)
    gender = fields.Selection(related='partner_id.gender', required=True)

    date_of_birth = fields.Date(
        string=u'Date of Birth',
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
    # street = fields.Char(related='partner_id.street', required=True)
    # zip = fields.Char(related='partner_id.zip', required=True)
    # city = fields.Char(related='partner_id.city', required=True)
    # country_id = fields.Many2one(related='partner_id.country_id', required=True)
    # phone = fields.Char(related='partner_id.phone', required=True)
    email = fields.Char(related='partner_id.email', required=True)


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
    photo_file_filename = fields.Char(
        string=u'photo_filename',
    )
    
    vita_file = fields.Binary('Curriculum Vitae', required=True)
    vita_file_filename = fields.Char(
        string=u'vita_filename',
    )
    
    passport_file = fields.Binary('Copy of Passport', required=True)
    passport_file_filename = fields.Char(
        string=u'passport_filename',
    )
    
    degrees_file = fields.Binary('Copies of degrees', required=True)
    degrees_file_filename = fields.Char(
        string=u'degrees_filename',
    )
    
    research_abstract_file = fields.Binary('Title and Abstract of intended research', required=True)
    research_abstract_file_filename = fields.Char(
        string=u'research_abstract_filename',
    )

    # PAYMENT FIELDS
    payment_method = fields.Selection(
        string=u'Payment Method',
        selection=[
            ('one_time', 'One-time payment'),
            ('two_times', 'Two-time payment'),
            ('three_times', 'Three-time payment'),
        ]
    )

    states = [
        ('new', 'New'),
        ('signed', 'Signed'),
        ('approved', 'Approved'),
        ('advisor_search', 'Advisor Search'),
        ('advisor_matched', 'Advisor Match'),
        ('advisor_found', 'Advisor agreed'),
        ('done', 'Done'),
        ('declined', 'Declined')
    ]
    # PROCESS FIELDS
    state = fields.Selection(
        states,
        'State', default='new', required=True, track_visibility='onchange', group_expand='_read_group_stage_ids'
    )
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return [k for k, v in self.states]

    @api.one
    def approved_registrar(self, record):
        self.write({'state' : 'approved'})

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        required=True,
        states={'done': [('readonly', True)]},
    )

    product_id = fields.Many2one(
        'product.product',
        'Product',
        domain=[('type', '=', 'service')],
    )

    application_fee_invoice_id = fields.Many2one(
        'account.invoice',
        'Application Fee Invoice',
    )

    @api.multi
    def write(self, values):
        if 'state' in values:
            states = [k for k, v in self.states]
            if abs(states.index(self.state) - states.index(values['state'])) > 1:
                raise ValidationError(_('You\'re not allowed to skip stages in this kanban!'))

            self.on_state_change(values['state'])

        super(GhuApplication, self).write(values)

    def on_creation(self, record):
        email_template = self.env.ref('ghu.ghu_new_doctoral_application_template')
        photo_id = self.env['ir.attachment'].create(
            {
                    'name': record.photo_file_filename,
                    'datas': record.photo_file,
                    'datas_fname': record.photo_file_filename,
                    'res_model': 'ghu.application',
                    'type': 'binary'
            }
        )
        cv_id = self.env['ir.attachment'].create(
            {
                    'name': record.vita_file_filename,
                    'datas': record.vita_file,
                    'datas_fname': record.vita_file_filename,
                    'res_model': 'ghu.application',
                    'type': 'binary'
            }
        )
        pp_id = self.env['ir.attachment'].create(
            {
                    'name': record.passport_file_filename,
                    'datas': record.passport_file,
                    'datas_fname': record.passport_file_filename,
                    'res_model': 'ghu.application',
                    'type': 'binary'
            }
        )
        degree_id = self.env['ir.attachment'].create(
            {
                    'name': record.degrees_file_filename,
                    'datas': record.degrees_file,
                    'datas_fname': record.degrees_file_filename,
                    'res_model': 'ghu.application',
                    'type': 'binary'
            }
        )
        abstract_id = self.env['ir.attachment'].create(
            {
                    'name': record.research_abstract_file_filename,
                    'datas': record.research_abstract_file,
                    'datas_fname': record.research_abstract_file_filename,
                    'res_model': 'ghu.application',
                    'type': 'binary'
            }
        )
        email_template.attachment_ids =  False
        email_template.attachment_ids = [(4, photo_id.id),(4, cv_id.id),(4, pp_id.id),(4, degree_id.id),(4, abstract_id.id)]
        email_template.send_mail(record.id, raise_exception=False, force_send=True)

        notification_template = self.env.ref('ghu.ghu_doctoral_application_confirmation_template')
        notification_template.send_mail(record.id, raise_exception=False, force_send=True)

    def on_state_change(self, new_state):
        # generate invoice
        if new_state == 'approved' and not self.application_fee_invoice_id:
            # get proper product
            product = self.env['product.product'].search([('id', '=', self.env['ir.config_parameter'].get_param('ghu.doctoral_application_fee_product'))])

            invoice_partners = self.partner_id.child_ids.filtered(lambda p: p.type == 'invoice')

            invoice = self.env['account.invoice'].create(dict(
                partner_id=invoice_partners[0].id if invoice_partners else self.partner_id.id, # customer (billing address)
                partner_shipping_id=self.partner_id.id, # customer (applicant)
                type='out_invoice',
                date_invoice=datetime.datetime.utcnow().date(), # invoice date
                date_due=(datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).date(), # due date
                user_id=self.env().user.id, # salesperson
                invoice_line_ids=[], # invoice lines
                name='Doctoral Program Application Fee', # name for account move lines
                # partner_bank_id=, # company bank account
            ))

            invoice_line = self.env['account.invoice.line'].with_context(
                    type=invoice.type, 
                    journal_id=invoice.journal_id.id, 
                    default_invoice_id=invoice.id
                ).create(dict(
                    product_id=product.id,
                    name='Doctoral Program Application Fee',
                    price_unit=product.lst_price,
                ))

            invoice.invoice_line_ids = [(4, invoice_line.id)]

            invoice.action_invoice_open()

            self.application_fee_invoice_id = invoice.id


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
