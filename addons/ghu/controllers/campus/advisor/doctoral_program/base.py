# -*- coding: utf-8 -*-
import base64
import json
import logging

from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class GhuDoctoralStudent(http.Controller):
    @http.route('/campus/advisor/doctoral-program/', type='http', auth='user', methods=['GET'], website=True)
    def showAllAdvisedDoctorands(self, **kwargs):
        
        # Show all doctorands of advisor
        return

    @http.route('/campus/advisor/doctoral-program/<model("ghu.doctoral_program"):obj>', type='http', auth='user', methods=['GET'], website=True)
    def showAdvisedDoctorand(self, obj, **kwargs):
        # Show the selected doctorands program
        return

    

