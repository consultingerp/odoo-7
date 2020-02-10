from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramSkills(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/skills', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsSkills(self, obj, **kwargs):
        # Show the selected doctorands program
        return
