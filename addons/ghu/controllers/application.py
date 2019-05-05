# -*- coding: utf-8 -*-
import base64
import json

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

class Ghu(http.Controller):
    @http.route('/ghu/create_application/', type='http', auth='public', methods=['POST'], website=True)
    def create_application(self, **kwargs):
        application_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu.application')])
        application_fields = request.env['ir.model.fields'].sudo().search([
            ('model_id', '=', application_model.id),
        ])

        required_fields = [f['name'] for f in application_fields if f['required'] and not f['related']]
        
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
                kwargs[(key[:-3] + '_filename')] = value.filename
                kwargs[key[:-3]] = base64.b64encode(value.read())

        # set default fields
        kwargs['state'] = 'new'
        # avoid missing field
        kwargs['partner_id'] = True

        # check missing fields
        missing_fields = [f for f in required_fields if f not in kwargs]
        if missing_fields:
            return json.dumps(dict(error_fields=missing_fields))

        # extract contact fields
        contact_data = dict()
        for f in contact_fields:
            contact_data[f] = kwargs.pop(f)

        # extract invoice fields
        invoice_data = dict()
        for f in invoice_fields:
            invoice_data[f[len('payment_')-1:]] = kwargs.pop(f)

        try:
            # create invoice address
            invoice_data['type'] = 'invoice'
            invoice_partner = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True).create(invoice_data)
            
            # create contact
            contact_data['child_ids'] = [invoice_partner.id]
            contact = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True).create(contact_data)

            # create application
            kwargs['partner_id'] = contact.id
            application_record = request.env['ghu.application'].sudo().with_context(mail_create_nosubscribe=True).create(kwargs)
            for study in studies.values():
                study['application_id'] = application_record.id
                request.env['ghu.application_study'].sudo().with_context(mail_create_nosubscribe=True).create(study)
        except IntegrityError:
            return json.dumps(False)

        return json.dumps(dict(id=application_record.id))
