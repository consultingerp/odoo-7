# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64

class GhuApplication(models.Model):
    _name = 'ghu.application'
    _description = 'GHU Application'
    _rec_name = 'last_name'

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
    payment_full_name = fields.Char('Payment Full Name', size=256, required=True)
    payment_street = fields.Char('Payment Street', size=256, required=True)
    payment_zip = fields.Char('Payment Zip', size=16, required=True)
    payment_city = fields.Char('Payment City', size=128, required=True)
    payment_country = fields.Many2one(
        'res.country', 'Payment Country', required=True)
    payment_phone = fields.Char('Payment Phone', size=64, required=True)
    payment_email = fields.Char('Payment Email', size=256, required=True)

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
    def _read_group_stage_ids(self,stages,domain,order):
        return [k for k, v in self.states]

    @api.one
    def approved_registrar(self, record):
        self.write({'state' : 'approved'})

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
    @api.one
    def create_sign_request(self, record):
        pdf = self.env.ref('ghu.application_agreement_pdf').sudo().render_qweb_pdf([self.id])[0]
        attachmentName = 'Application-'+self.last_name+'-'+str(self.id)+'.pdf'
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
                'template_id' : template.id,
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
        res = self.env['sign.request'].sudo().initialize_new(
            template.id,
            [
                {'role': self.env.ref('sign.sign_item_role_customer').id, 'partner_id': self.partner_id.id}
            ],
            [],
            'Your Application at GHU - ' + self.partner_id.lastname,
            'Your Application at GHU - ' + self.partner_id.lastname,
            "<p>We are pleased to inform you, " + self.partner_id.firstname + ", that we have successfully received your application at the Global Humanistic University.</p><p>There is only one step left to finish it, so please sign the document via the link below to start the application processing on our side.<p><br></p><p>Global Humanistic University</p>",
            True
        )

    def on_creation(self, record):
        self.create_sign_request(record)

    def signed_by_applicant(self, record):
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
