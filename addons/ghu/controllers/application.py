# -*- coding: utf-8 -*-
import base64
import json
import logging

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class Ghu(http.Controller):
    @http.route('/ghu/create_application/', type='http', auth='public', methods=['POST'], website=True)
    def create_application(self, **kwargs):
        application_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu.application')])
        application_fields = request.env['ir.model.fields'].sudo().search([
            ('model_id', '=', application_model.id),
        ])
        application_study_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu.application_study')])
        application_study_fields = request.env['ir.model.fields'].sudo().search([
            ('model_id', '=', application_study_model.id),
        ])

        required_fields = [f['name'] for f in application_fields if f['required'] and not f['related']]
        required_study_fields = [f['name'] for f in application_study_fields if f['required'] and not f['related']]
        
        # add required fields for partner
        contact_fields = [
            'firstname',
            'lastname',
            'gender',
            'street',
            'zip',
            'city',
            'country_id',
            'phone',
            'email',
        ]
        required_fields += contact_fields
        invoice_fields = [
            'payment_name',
            'payment_street',
            'payment_zip',
            'payment_city',
            'payment_country_id',
            'payment_phone',
            'payment_email',
        ]
        required_fields += invoice_fields

        # extract studies-* args and files
        studies = dict()
        for key in list(kwargs.keys()):
            if key.startswith('studies-'):
                parts = key.split('-')
                index = parts[-1]
                if index not in studies:
                    studies[index] = dict()
                studies[index][parts[1]] = kwargs.pop(key)
                continue

            if hasattr(kwargs[key], 'filename'):
                value = kwargs.pop(key)
                kwargs[(key[:-6] + '_filename')] = value.filename
                kwargs[key[:-6]] = base64.b64encode(value.read())

        # set default fields
        kwargs['state'] = 'new'
        # avoid missing field
        kwargs['partner_id'] = True

        # check missing fields
        missing_fields = dict()
        for f in required_fields:
            if f not in kwargs:
                missing_fields[f] = True
        _logger.info(studies)
        for idx, study in studies.items():
            for f in required_study_fields:
                if f not in study:
                    missing_fields['studies-' + f + '-' + str(idx)] = True
        if missing_fields:
            request.env['mail.message'].sudo().create({'message_type':"notification",
                "subtype": request.env.ref("mail.mt_comment").id,
                'body': "Application failed<br/><br/>Missing fields:<br/>" + str(missing_fields),
                'subject': "Application failed",
                'needaction_partner_ids': [(4, 3)]
            })
            return json.dumps(dict(error_fields=missing_fields))

        # extract contact fields
        contact_data = dict()
        for f in contact_fields:
            contact_data[f] = kwargs.pop(f)

        # extract invoice fields
        invoice_data = dict(type='invoice')
        for f in invoice_fields:
            invoice_data[f[len('payment_'):]] = kwargs.pop(f)

        # preprocess fields
        kwargs['ever_applied_at_ghu'] = bool(int(kwargs['ever_applied_at_ghu']))
        kwargs['ever_applied_doctoral'] = bool(int(kwargs['ever_applied_doctoral']))
        if 'other_languages' in kwargs.keys():
            kwargs['other_languages'] = [(4, l) for l in kwargs['other_languages'].split(',')]

        try:
            # create contact
            contact_data['child_ids'] = [(0, 0, invoice_data)] # create invoice address implicit
            contact = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True).create(contact_data)

            # create application
            kwargs['partner_id'] = contact.id
            application_record = request.env['ghu.application'].sudo().with_context(mail_create_nosubscribe=True).create(kwargs)
            for study in studies.values():
                study['application_id'] = application_record.id
                request.env['ghu.application_study'].sudo().with_context(mail_create_nosubscribe=True).create(study)
            application_record.message_subscribe([contact.id])
            application_record.message_subscribe_user([2,6,8,11,44])
        except IntegrityError as e:
            request.env['mail.message'].sudo().create({'message_type':"notification",
                "subtype": request.env.ref("mail.mt_comment").id,
                'body': "Application failed<br/><br/>Integrity Error:<br/>" + str(e),
                'subject': "Application failed",
                'needaction_partner_ids': [(4, 3)]
            })
            return json.dumps(False)

        return json.dumps(dict(id=application_record.id))
