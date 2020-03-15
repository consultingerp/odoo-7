# -*- coding: utf-8 -*-
import base64
import json
from datetime import datetime
from datetime import timedelta
from sqlite3 import IntegrityError

from odoo import http
from odoo.http import request


class GhuMsc(http.Controller):
    @http.route('/msc/application/', type='http', auth='public', methods=['GET', 'POST'], website=True)
    def render_application(self, **kwargs):
        if request.httprequest.method == 'GET':
            return http.request.render('ghu_msc.apply_msc', {})
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

            # extract contact fields
            contact_data = dict()
            for f in contact_fields:
                contact_data[f] = kwargs.pop(f)

            if 'other_languages' in kwargs.keys():
                # preprocess fields
                kwargs['other_languages'] = [(4, l) for l in kwargs['other_languages'].split(',')]

            for key in list(kwargs.keys()):
                if hasattr(kwargs[key], 'filename'):
                    value = kwargs.pop(key)
                    kwargs[(key[:-6] + '_filename')] = value.filename
                    kwargs[key[:-6]] = base64.b64encode(value.read())

            try:
                # check if contact exists
                contact = request.env['res.partner'].sudo().search([('email', '=', contact_data['email'])], limit=1)

                if contact:
                    contact.update(contact_data)
                else:
                    # create contact
                    contact = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True).create(
                        contact_data)

                # create application
                kwargs['partner_id'] = contact.id
                # create application
                application_record = request.env['ghu_msc.application'].sudo().with_context(
                    mail_create_nosubscribe=True).create(
                    kwargs)
                # Add floris to follower
                application_record.message_subscribe([11], [])
                self.env['mail.activity'].sudo().create({
                    'res_model_id': self.env.ref('ghu_msc.application').id,
                    'res_id': application_record.id,
                    'user_id': 11,
                    'activity_type_id': self.env.ref('ghu_msc.ghu_activity_data_check_msc_prerequisites').id,
                    'summary': 'Check requirements for MSc',
                    'date_deadline': datetime.now() + timedelta(days=7),
                })
            except IntegrityError:
                return json.dumps(False)

            return json.dumps(dict(id=application_record.id))

    @http.route('/msc/application/thank-you', type='http', auth='public', methods=['GET'], website=True)
    def thank_you(self):
        return http.request.render('ghu_msc.apply_thankyou', {})
