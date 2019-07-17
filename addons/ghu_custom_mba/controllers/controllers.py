# -*- coding: utf-8 -*-
from odoo import http
import json

class GhuCustomMba(http.Controller):
    @http.route('/campus/course/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/campus/course/objects/', auth='public', website=True)
    def list(self, **kw):
        return http.request.render('ghu_custom_mba.courselist', {
            'root': '/campus/course',
            'objects': http.request.env['ghu_custom_mba.course'].search([]),
        })

    @http.route('/campus/course/objects/<model("ghu_custom_mba.course"):obj>/', auth='public', website=True)
    def object(self, obj, **kw):
        return http.request.render('ghu_custom_mba.coursedetail', {
            'object': obj
        })
    
    @http.route('/campus/course/objects/<model("ghu_custom_mba.course"):obj>/edit', auth='public', website=True)
    def edit(self, obj, **kw):
        return http.request.render('ghu_custom_mba.courseedit', {
            'object': obj
        })
    
    @http.route('/api/campus/course/objects/<model("ghu_custom_mba.course"):obj>/', auth='public', website=True, type="json")
    def apiObject(self, obj, **kw):
        return json.dumps(obj)