from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusAdvisorDoctoralProgramReflection(http.Controller):
    
    @http.route('/campus/advisor/doctoral-program/<model("ghu.doctoral_program"):obj>/reflection/', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsReflection(self, obj, **kwargs):
        obj = request.env['ghu.doctoral_program'].sudo().browse(obj.id)
        # Show the selected doctorands program
        partner_id = request.env.user.partner_id.id
        advisor = request.env['ghu.advisor'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        if obj.advisor_ref.id == advisor.id:
            return http.request.render('ghu.campus_advisor_doctoral_program_reflection', {
                'program': obj
            })
        return http.request.not_found()