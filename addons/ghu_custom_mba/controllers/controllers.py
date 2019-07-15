# -*- coding: utf-8 -*-
from odoo import http

class GhuCustomMba(http.Controller):
    @http.route('/campus/course/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/campus/course/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('course.listing', {
            'root': '/ghu_custom_mba/course',
            'objects': http.request.env['ghu_custom_mba.course'].search([]),
        })

    @http.route('/campus/course/objects/<model("ghu_custom_mba.course"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('course.object', {
            'object': obj
        })