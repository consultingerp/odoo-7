# -*- coding: utf-8 -*-

import datetime
import logging
import base64
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

    research_abstract_file = fields.Binary(
        'Title and Abstract of intended research', required=True)
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

    # Thesis title
    thesis_title = fields.Char(
        string='Thesis Title',
        required=False,
        help='Will be printed in student-advisor agreement'
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


    first_fee_invoice_id = fields.Many2one(
        'account.invoice',
        'First Fee Invoice',
    )

    sign_request_id = fields.Many2one(
        'sign.request',
        'Sign Request',
        states={'done': [('readonly', True)]},
    )

    agreement_request_id = fields.Many2one(
        'sign.request',
        'Student-Advisor Agreement',
        states={'done': [('readonly', True)]},
    )

    advisor_ref = fields.Reference(
        string=u'Advisor',
        selection=[('ghu.advisor', 'Advisor')]
    )

    advisor_matching_count = fields.Integer(
        string=u'Advisor Matching Count',
    )

    @api.multi
    def write(self, values):
        if 'state' in values:
            states = [k for k, v in self.states]
            if abs(states.index(self.state) - states.index(values['state'])) > 1:
                raise ValidationError(
                    _('You\'re not allowed to skip stages in this kanban!'))

            self.on_state_change(values['state'])
        super(GhuApplication, self).write(values)

    def on_creation(self, record):
        self_sudo = self.sudo(self.env['res.users'].sudo().search(
            [('email', 'like', 'office@ghu.edu.cw')], limit=1))
        self_sudo.create_sign_request(record)

    @api.one
    def create_sign_request(self, record):
        self = self.sudo()
        pdf = self.env.ref(
            'ghu.application_agreement_pdf').render_qweb_pdf([self.id])[0]
        attachmentName = 'Application-'+self.lastname+'-'+str(self.id)+'.pdf'
        attachment = self.env['ir.attachment'].create({
            'name': attachmentName,
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': attachmentName,
            'res_model': 'ghu.application',
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        template = self.env['sign.template'].create(
            {
                'attachment_id': attachment.id,
                'active': 'true'
            }
        )
        signature = self.env['sign.item'].create(
            {
                'template_id': template.id,
                'height': 0.05,
                'name': "Signature",
                'page': "1",
                'posX': 0.766,
                'posY': 0.042,
                'required': 'true',
                'responsible_id': 1,
                'type_id': 1,
                'width': 0.2
            }
        )
        res = self.env['sign.request'].initialize_new(
            template.id,
            [
                {'role': self.env.ref(
                    'sign.sign_item_role_customer').id, 'partner_id': self.partner_id.id}
            ],
            [],
            'Application finalization',
            'Your Application at GHU',
            '<p>We are pleased to inform you, ' + self.partner_id.firstname +
            ', that we have successfully received your application at the Global Humanistic University.</p><p>There is only your signature missing, so please sign the document via the link below to start the application processing on our side.<p><br></p><p>Global Humanistic University</p>',
            True
        )
        sign_request = self.env['sign.request'].browse(res['id'])
        sign_request.toggle_favorited()
        sign_request.action_sent()
        sign_request.write({'state': 'sent'})
        sign_request.request_item_ids.write({'state': 'sent'})

        application = self.env['ghu.application'].browse(self.id)
        application.sign_request_id = sign_request.id

    @api.one
    def create_agreement_request(self):
        self = self.sudo()
        pdf = self.env.ref(
            'ghu.student_advisor_agreement_pdf').render_qweb_pdf([self.id])[0]
        attachmentName = 'Agreement-'+self.lastname+'-'+str(self.id)+'.pdf'
        attachment = self.env['ir.attachment'].create({
            'name': attachmentName,
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': attachmentName,
            'res_model': 'ghu.application',
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        template = self.env['sign.template'].create(
            {
                'attachment_id': attachment.id,
                'active': 'true'
            }
        )
        signature_student = self.env['sign.item'].create(
            {
                'template_id': template.id,
                'height': 0.05,
                'name': "Signature",
                'page': "2",
                'posX': 0.166,
                'posY': 0.142,
                'required': 'true',
                'responsible_id': self.env.ref(
                    'ghu.sign_item_role_student').id,
                'type_id': 1,
                'width': 0.2
            }
        )
        signature_advisor = self.env['sign.item'].create(
            {
                'template_id': template.id,
                'height': 0.05,
                'name': "Signature",
                'page': "2",
                'posX': 0.166,
                'posY': 0.242,
                'required': 'true',
                'responsible_id': self.env.ref(
                    'ghu.sign_item_role_advisor').id,
                'type_id': 1,
                'width': 0.2
            }
        )
        res = self.env['sign.request'].initialize_new(
            template.id,
            [
                {'role': self.env.ref(
                    'ghu.sign_item_role_student').id, 'partner_id': self.partner_id.id},
                {'role': self.env.ref(
                    'ghu.sign_item_role_advisor').id, 'partner_id': self.advisor_ref.partner_id.id}
            ],
            [],
            'Advisor-Student-Agreement',
            'Advisor-Student-Agreement at GHU',
            '<p>We are pleased to inform you, ' + self.partner_id.firstname +
            ', that we have successfully found your advisor for your doctoral program.</p><p>There is only your signature missing, so please sign the document via the link below to finish the application processing on your side.<p><br></p><p>Global Humanistic University</p>',
            True
        )
        sign_request = self.env['sign.request'].browse(res['id'])
        sign_request.toggle_favorited()
        sign_request.action_sent()
        sign_request.write({'state': 'sent'})
        sign_request.request_item_ids.write({'state': 'sent'})

        application = self.env['ghu.application'].browse(self.id)
        application.agreement_request_id = sign_request.id

    def on_state_change(self, new_state):
        # generate invoice
        self_sudo = self.sudo()
        if new_state == 'signed':
            self_sudo.signed_by_applicant()
        elif new_state == 'approved' and not self.application_fee_invoice_id:
            self_sudo.send_application_fee_invoice()
        elif new_state == 'advisor_search' and self.state == '':
            self_sudo.send_advisor_search_notification()
        elif new_state == 'advisor_matched':
            self_sudo.notify_advisor()
        elif new_state == 'advisor_found':
            self_sudo.create_agreement_request()
            self_sudo.send_first_fee_invoice()
        elif new_state == 'done':
            self_sudo.finish_application()
        elif new_state == 'declined':
            self_sudo.end_application()

    def signed_by_applicant(self, record):
        # attach signed pdf to mail
        email_template = self.env.ref(
            'ghu.ghu_new_doctoral_application_template')

        application_id = self.env['ir.attachment'].create(
            {
                'name': "Application",
                'datas': record.sign_request_id.completed_document,
                'datas_fname': "application.pdf",
                'res_model': 'ghu.application',
                'type': 'binary'
            }
        )

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
        email_template.attachment_ids = False
        email_template.attachment_ids = [(4, application_id.id), (4, photo_id.id), (
            4, cv_id.id), (4, pp_id.id), (4, degree_id.id), (4, abstract_id.id)]
        email_template.send_mail(
            record.id, raise_exception=False, force_send=False)

        notification_template = self.env.ref(
            'ghu.ghu_doctoral_application_confirmation_template')
        notification_template.send_mail(
            record.id, raise_exception=False, force_send=False)

    def send_application_fee_invoice(self):
        # get proper product
        product = self.env['product.product'].search(
            [('id', '=', self.env['ir.config_parameter'].get_param('ghu.doctoral_application_fee_product'))])

        invoice_partners = self.partner_id.child_ids.filtered(
            lambda p: p.type == 'invoice')

        invoice = self.env['account.invoice'].create(dict(
            # customer (billing address)
            partner_id=invoice_partners[0].id if invoice_partners else self.partner_id.id,
            partner_shipping_id=self.partner_id.id,  # customer (applicant)
            type='out_invoice',
            date_invoice=datetime.datetime.utcnow().date(),  # invoice date
            date_due=(datetime.datetime.utcnow() + \
                      datetime.timedelta(weeks=1)).date(),  # due date
            user_id=self.env().user.id,  # salesperson
            invoice_line_ids=[],  # invoice lines
            name='Doctoral Program Application Fee',  # name for account move lines
            partner_bank_id=self.env['ir.config_parameter'].get_param(
                'ghu.automated_invoice_bank_account'),  # company bank account
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

        invoice_template = self.env.ref('ghu.ghu_invoice_email_template')
        invoice_template.send_mail(invoice.id)
        invoice.write({'sent': True})

        self.application_fee_invoice_id = invoice.id

    def send_advisor_search_notification(self):
        email_template = self.env.ref(
            'ghu.mail_application_advisor_search_notification')
        email_template.send_mail(
            self.id, raise_exception=False, force_send=False)

    def notify_advisor(self):
        email_template = self.env.ref(
            'ghu.mail_application_notify_advisor')
        email_template.send_mail(
            self.id, raise_exception=False, force_send=False)

    def send_first_fee_invoice(self):
        invoice_partners = self.partner_id.child_ids.filtered(
            lambda p: p.type == 'invoice')
        invoice = self.env['account.invoice'].create(dict(
            # customer (billing address)
            partner_id=invoice_partners[0].id if invoice_partners else self.partner_id.id,
            # customer (applicant)
            partner_shipping_id=self.partner_id.id,
            type='out_invoice',
            date_invoice=datetime.datetime.utcnow().date(),  # invoice date
            date_due=(datetime.datetime.utcnow() + \
                      datetime.timedelta(weeks=1)).date(),  # due date
            user_id=1,  # salesperson
            invoice_line_ids=[],  # invoice lines
            name="First payment",  # name for account move lines
            partner_bank_id=self.env['ir.config_parameter'].get_param(
                'ghu.automated_invoice_bank_account'),  # company bank account
        ))

        if self.payment_method == 'one_time':
            payment = 24500
        elif self.payment_method == 'two_times':
            payment = 12500
        else:
            payment = 9000

        product = self.env['product.product'].search(
            [('id', '=', self.env['ir.config_parameter'].get_param('ghu.doctoral_application_fee_product'))])
        invoice_line = self.env['account.invoice.line'].sudo().with_context(
            type=invoice.type,
            journal_id=invoice.journal_id.id,
            default_invoice_id=invoice.id
        ).create(dict(
            product_id=product.id,
            name="First Fee",
            price_unit=payment,
        ))

        invoice.invoice_line_ids = [(4, invoice_line.id)]
        invoice.action_invoice_open()
        invoice_template = self.env.ref(
            'ghu.ghu_invoice_email_template').sudo()
        invoice_template.send_mail(invoice.id)
        invoice.write({'sent': True})

        self.first_fee_invoice_id = invoice.id


    # Check if signed request is one of an application
    def check_signature(self, record):
        if record.state == "signed":
            application = self.search([('sign_request_id', '=', record.id)])
            if application:
                if application.state == "new":
                    application.write({'state': 'signed'})
            application = self.search([('agreement_request_id', '=', record.id)])
            if application:
                if application.state == "advisor_found" and application.first_fee_invoice_id.state == 'paid':
                    application.write({'state': 'done'})

    # Check if paid invoice is one of an application
    def check_invoice(self, record):
        if record.state == "paid":
            application = self.search(
                [('application_fee_invoice_id', '=', record.id)])
            if application:
                if application.state == "approved":
                    application.write({'state': 'advisor_search'})
            application = self.search(
                [('first_fee_invoice_id', '=', record.id)])
            if application:
                if application.state == "advisor_found" and application.agreement_request_id.state == 'signed':
                    application.write({'state': 'done'})

    @api.one
    def approved_registrar(self, record):
        self_sudo = self.sudo()
        self_sudo.write({'state': 'approved'})

    @api.one
    def advisor_has_matched(self):
        self_sudo = self.sudo()
        self_sudo.write(
            {
                'advisor_matching_count': self.advisor_matching_count+1,
                'state': 'advisor_matched'
            }
        )

    @api.one
    def advisor_has_approved(self):
        self_sudo = self.sudo()
        self_sudo.write({'state': 'advisor_found'})

    @api.one
    def advisor_has_declined(self):
        self_sudo = self.sudo()
        if self.advisor_matching_count < 2:
            self_sudo.write({'state': 'advisor_search'})
        else:
            self_sudo.write({'state': 'declined'})


class GhuApplicationStudy(models.Model):
    _name = 'ghu.application_study'
    _description = 'GHU Application Preliminary Studies'
    _log_access = False

    institution = fields.Char('Institution', size=256, required=True)
    city = fields.Char('City', size=128, required=False)
    from_date = fields.Date(
        string=u'From', required=False
    )
    to_date = fields.Date(
        string=u'To', required=False
    )
    subject = fields.Char('Subject', size=256, required=True)
    diploma = fields.Char('Diploma', size=256, required=True)
    credit_points = fields.Integer('Credit Points', required=False)

    application_id = fields.Many2one(
        'ghu.application',
        string='GHU Application',
    )
