# -*- coding: utf-8 -*-
import base64
import json
import logging

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GhuDoctoralStudent(http.Controller):
    @http.route('/campus/student/doctoral-program/', type='http', auth='user', methods=['GET'], website=True)
    def showAllDoctoralPrograms(self, **kwargs):
        # Show all doctorands of student
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        programs = request.env['ghu.doctoral_program'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id))])
        if programs:
            return http.request.render('ghu.campus_student_doctoral_program_list', {
                'programs': programs
            })
        return http.request.not_found()

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>', type='http', auth='user', methods=['GET'], website=True)
    def showProgram(self, obj, **kwargs):
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            return http.request.render('ghu.campus_student_doctoral_program_overview', {
                'program': obj
            })
        return http.request.not_found()

    

