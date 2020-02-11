from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramProposal(http.Controller):
    
    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/proposal/', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsResearchProposal(self, obj, **kwargs):
        # Show the selected doctorands program
        return