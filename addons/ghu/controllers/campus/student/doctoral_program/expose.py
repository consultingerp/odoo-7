from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusStudentDoctoralProgramExpose(http.Controller):

    @http.route('/campus/student/doctoral-program/<model("ghu.doctoral_program"):obj>/expose', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsExpose(self, obj, **kwargs):
        # Show the selected doctorands program
        return