from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GhuCampusAdvisorDoctoralProgramDefensio(http.Controller):

    @http.route('/campus/advisor/doctoral-program/<model("ghu.doctoral_program"):obj>/defensio', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorandsDefensio(self, obj, **kwargs):
        # Show the selected doctorands program
        return