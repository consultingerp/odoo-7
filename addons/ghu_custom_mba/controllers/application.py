# -*- coding: utf-8 -*-
import base64
import json
import logging

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GhuCustomMba(http.Controller):
    @http.route('/custom-mba/application/', type='http', auth='public', methods=['GET'], website=True)
    def render_application(self, **kwargs):
        return http.request.render('ghu_custom_mba.apply_custom_mba', {})

    @http.route('/campus/apply_custom_mba/', type='http', auth='public', methods=['POST'], website=True)
    def apply_custom_mba(self, **kwargs):
        student_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu.student')])
        student_fields = request.env['ir.model.fields'].sudo().search([
            ('model_id', '=', student_model.id),
        ])

        required_fields = [f['name'] for f in student_fields if f['required'] and not f['related']]
        
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

        if 'other_languages' in kwargs.keys():
            # preprocess fields
            kwargs['other_languages'] = [(4, l) for l in kwargs['other_languages'].split(',')]

        try:
            # check if student already exists, if yes do not allow creation again
            student = request.env['ghu.student'].sudo().search([('email','=',contact_data['email'])], limit=1)
            if student:
                return json.dumps(dict(error_fields=['email']))
            # check if contact exists
            contact = request.env['res.partner'].sudo().search([('email','=',contact_data['email'])], limit=1)
            
            if contact:
                contact.update(contact_data)
            else:
                # create contact
                contact = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True).create(contact_data)

            # Add floris to follower
            contact.message_subscribe([11], [])
            # create application
            kwargs['partner_id'] = contact.id
            kwargs['custom_mba'] = True
            student_record = request.env['ghu.student'].sudo().with_context(mail_create_nosubscribe=True).create(kwargs)
            student_record.applicationReceived()
        except IntegrityError:
            return json.dumps(False)


        return json.dumps(dict(id=student_record.id))


    @http.route('/campus/apply-custom-mba/thank-you', type='http', auth='public', methods=['GET'], website=True)
    def thank_you(self):
        return http.request.render('ghu_custom_mba.apply_custom_mba_thankyou', {})
