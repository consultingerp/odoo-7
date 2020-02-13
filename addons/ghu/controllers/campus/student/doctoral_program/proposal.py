from odoo import http
from odoo.http import request
import logging
import base64
import werkzeug

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramProposal(http.Controller):
    
    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/proposal/', type='http', auth='user', methods=['GET'], website=True)
    def showDoctorandsResearchProposal(self, obj, **kwargs):
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            return http.request.render('ghu.campus_student_doctoral_program_proposal', {
                'program': obj
            })
        return http.request.not_found()

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/proposal/', type='http', auth="user", methods=['POST'], website=True)
    def saveDoctorandsProposal(self, obj, **post):
        obj = request.env['ghu.doctoral_program'].sudo().browse(obj.id)
        partner_id = request.env.user.partner_id.id
        student = request.env['ghu.student'].sudo().search(
            [('partner_id', '=', partner_id)], limit=1)
        if obj.student_ref.id == student.id:
            if not obj.proposal_id:
                if post.get('attachment', False):
                    name = post.get('attachment').filename
                    file = post.get('attachment')
                    attachmentData = file.read()
                    proposal = request.env['ghu.doctoral_program_professional_capability'].sudo().create(
                        {
                            'attachment': base64.encodestring(attachmentData),
                            'attachment_filename': name
                        }
                    )
                    obj.write({
                        'proposal_id': proposal.id
                    })
                    return werkzeug.utils.redirect('/campus/student/doctoral-program/'+str(obj.id))
        return http.request.not_found()