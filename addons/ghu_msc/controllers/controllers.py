# -*- coding: utf-8 -*-
import base64
import json
from sqlite3 import IntegrityError

from odoo import http
from odoo.http import request

class GhuMsc(http.Controller):
    @http.route('/msc/application/', type='http', auth='public', methods=['GET', 'POST'], website=True)
    def render_application(self, **kwargs):
        if request.httprequest.method == 'GET':
            return http.request.render('ghu_custom_mba.apply_custom_mba', {})
        if request.httprequest.method == 'POST':
            msc_application_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu.student')])
            msc_application_fields = request.env['ir.model.fields'].sudo().search([
                ('model_id', '=', msc_application_model.id),
            ])

            required_fields = [f['name'] for f in msc_application_fields if f['required'] and not f['related']]

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

            # check missing fields
            missing_fields = [f for f in required_fields if f not in kwargs]
            if missing_fields:
                return json.dumps(dict(error_fields=missing_fields))

            if 'other_languages' in kwargs.keys():
                # preprocess fields
                kwargs['other_languages'] = [(4, l) for l in kwargs['other_languages'].split(',')]

            for key in list(kwargs.keys()):
                if hasattr(kwargs[key], 'filename'):
                    value = kwargs.pop(key)
                    kwargs[(key[:-6] + '_filename')] = value.filename
                    kwargs[key[:-6]] = base64.b64encode(value.read())

            try:
                # create application
                application_record = request.env['ghu_msc.application'].sudo().with_context(mail_create_nosubscribe=True).create(
                    kwargs)
                # Add floris to follower
                application_record.message_subscribe([11], [])
                application_record.applicationReceived()
            except IntegrityError:
                return json.dumps(False)

            return json.dumps(dict(id=application_record.id))


    @http.route('/msc/application/thank-you', type='http', auth='public', methods=['GET'], website=True)
    def thank_you(self):
        return http.request.render('ghu_custom_mba.apply_custom_mba_thankyou', {})