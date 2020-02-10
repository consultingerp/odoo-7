from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramDissertation(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/dissertation', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsDissertation(self, obj, **kwargs):
        # Show the selected doctorands program
        return