from odoo import http
from odoo.http import request
import logging
import base64
import werkzeug
_logger = logging.getLogger(__name__)


class GhuCampusStudentDoctoralProgramSkills(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/skills/', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsSkills(self, obj, **kwargs):
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search(
            [('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            return http.request.render('ghu.campus_student_doctoral_program_skills', {
                'program': obj
            })
        return http.request.not_found()

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/skills/', type='http', auth="user", methods=['POST'], website=True)
    def saveDoctorandsSkills(self, obj, **post):
        self_sudo = self.sudo()
        obj = self_sudo.env['ghu.doctoral_program'].browse(obj.id)
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search(
            [('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            if not obj.skills_id:
                if post.get('attachment', False):
                    name = post.get('attachment').filename
                    file = post.get('attachment')
                    attachmentData = file.read()
                    attachment = self_sudo.env['ir.attachment'].create({
                        'name': name,
                        'type': 'binary',
                        'datas': base64.encodestring(attachmentData),
                        'datas_fname': name,
                        'res_model': 'ghu.doctoral_program_academic_writing',
                        'mimetype': 'application/x-pdf'
                    })
                    skills = self_sudo.env['ghu.doctoral_program_academic_writing'].create(
                        {
                            'attachment': attachment.id
                        }
                    )
                    obj.write({
                        'skills_id': skills.id
                    })
                    return werkzeug.utils.redirect('/campus/student/doctoral-program/'+str(obj.id))
        return http.request.not_found()
