# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
import base64
import werkzeug
from ..util.blti import GhuBlti

_logger = logging.getLogger(__name__)


class GhuCustomMbaStudent(http.Controller):

    @http.route('/campus/courses/', auth='user', website=True)
    def list(self, **kw):
        return http.request.render('ghu_custom_mba.student_courselist', {
            'root': '/campus/course',
            'objects': http.request.env['ghu_custom_mba.course'].search([('state', '=','approved')]),
        })

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def preview(self, obj, **kw):
        if obj.state == 'approved':
            return http.request.render('ghu_custom_mba.student_coursepreview', {
                'root': '/campus/course',
                'object': obj,
                'slug': 'campus_courses'
            })
        return http.request.not_found()
