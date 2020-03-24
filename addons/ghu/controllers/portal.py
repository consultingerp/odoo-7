# -*- coding: utf-8 -*-

import odoo.addons.portal.controllers.portal as portal
import datetime
import pytz
import base64
from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(portal.CustomerPortal):
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "interest_id", "image", "skype"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post:
            if 'interest_id' in post:
                interest_id = [(6, 0, [int(interest) for interest in request.httprequest.form.getlist('interest_id')])]
                post.update({'interest_id': interest_id})
            if 'image' in post and post.get('image'):
                image = post.get('image')
                image_attachment = image.read()
                image = base64.b64encode(image_attachment)
                post.update({'image': image})
            else:
                post.pop('image')
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                values.update({
                    'error': {},
                    'error_message': [],
                })
                # if redirect:
                #    return request.redirect(redirect)
                # return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        interests = request.env['ghu.partner.interest'].sudo().search([])

        values.update({
            'partner': partner,
            'interests': interests,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
