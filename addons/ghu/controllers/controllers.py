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

        required_fields = [f for f in application_fields if f['required']]

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
                kwargs[key[:-3]] = base64.b64encode(value.read())

        # set default fields
        kwargs['state'] = 'new'

        # check missing fields
        missing_fields = [f['name'] for f in required_fields if f['name'] not in kwargs]
        if missing_fields:
            return json.dumps(dict(error_fields=missing_fields))

        try:
            application_record = request.env['ghu.application'].sudo().with_context(mail_create_nosubscribe=True).create(kwargs)
            for study in studies.values():
                study['application_id'] = application_record.id
                request.env['ghu.application_study'].sudo().with_context(mail_create_nosubscribe=True).create(study)
        except IntegrityError:
            return json.dumps(False)

        return json.dumps('hahahaa')

    # @http.route('/ghu/ghu/', auth='public')
    # def index(self, **kw):
    #     return 'Hello, world'

    # @http.route('/ghu/ghu/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('ghu.listing', {
    #         'root': '/ghu/ghu',
    #         'objects': http.request.env['ghu.ghu'].search([]),
    #     })

    # @http.route('/ghu/ghu/objects/<model('ghu.ghu'):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('ghu.object', {
    #         'object': obj
    #     })