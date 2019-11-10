# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
import base64
import werkzeug
from ..util.blti import GhuBlti

_logger = logging.getLogger(__name__)


class GhuCustomMbaHelp(http.Controller):
    @http.route('/campus/help/', auth='user', website=True)
    def list(self, **kw):
        return http.request.render('ghu_custom_mba.helpcenter', {
            'root': '/campus/course'
        })