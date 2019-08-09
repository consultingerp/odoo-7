# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
import base64
import werkzeug

_logger = logging.getLogger(__name__)

class GhuIdp(http.Controller):
    @http.route('/saml/course/', auth='user')
    def index(self, **kw):
        return "Hello, world"