# -*- coding: utf-8 -*-
import base64
import json
import logging

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GhuDoctoralStudent(http.Controller):
    @http.route('/campus/advisor/doctoral-program/', type='http', auth='user', methods=['GET'], website=True)
    def showAllAdvisedDoctorands(self, **kwargs):
        # Show all doctorands of advisor
        partner_id = request.env.user.partner_id.id
        advisor = request.env['ghu.advisor'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        programs = request.env['ghu.doctoral_program'].sudo().search(
                [('advisor_ref', '=', 'ghu.advisor,'+str(advisor.id))])
        if programs:
            return http.request.render('ghu.campus_advisor_doctoral_program_list', {
                'programs': programs
            })
        return http.request.not_found()

    @http.route('/campus/advisor/doctoral-program/<model("ghu.doctoral_program"):obj>', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorand(self, obj, **kwargs):
        obj = request.env['ghu.doctoral_program'].sudo().browse(obj.id)
        # Show the selected doctorands program
        partner_id = request.env.user.partner_id.id
        advisor = request.env['ghu.advisor'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        if obj.advisor_ref.id == advisor.id:
            return http.request.render('ghu.campus_advisor_doctoral_program_overview', {
                'program': obj
            })
        return http.request.not_found()
    

