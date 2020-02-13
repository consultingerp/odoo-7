from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramSkills(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/skills/', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsSkills(self, obj, **kwargs):
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            return http.request.render('ghu.campus_student_doctoral_program_skills', {
                'program': obj
            })
        return http.request.not_found()
