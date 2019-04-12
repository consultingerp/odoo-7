# -*- coding: utf-8 -*-
from odoo import http

# class Ghu(http.Controller):
#     @http.route('/ghu/ghu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ghu/ghu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ghu.listing', {
#             'root': '/ghu/ghu',
#             'objects': http.request.env['ghu.ghu'].search([]),
#         })

#     @http.route('/ghu/ghu/objects/<model("ghu.ghu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ghu.object', {
#             'object': obj
#         })