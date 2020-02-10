from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramPaper(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/paper', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsPaper(self, obj, **kwargs):
        # Show the selected doctorands program
        return