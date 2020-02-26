# -*- coding: utf-8 -*-
from odoo import http

# class GhuCampusStyle(http.Controller):
#     @http.route('/ghu_campus_style/ghu_campus_style/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ghu_campus_style/ghu_campus_style/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ghu_campus_style.listing', {
#             'root': '/ghu_campus_style/ghu_campus_style',
#             'objects': http.request.env['ghu_campus_style.ghu_campus_style'].search([]),
#         })

#     @http.route('/ghu_campus_style/ghu_campus_style/objects/<model("ghu_campus_style.ghu_campus_style"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ghu_campus_style.object', {
#             'object': obj
#         })