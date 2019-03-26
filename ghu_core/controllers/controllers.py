# -*- coding: utf-8 -*-
from odoo import http

# class GhuCore(http.Controller):
#     @http.route('/ghu_core/ghu_core/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ghu_core/ghu_core/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ghu_core.listing', {
#             'root': '/ghu_core/ghu_core',
#             'objects': http.request.env['ghu_core.ghu_core'].search([]),
#         })

#     @http.route('/ghu_core/ghu_core/objects/<model("ghu_core.ghu_core"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ghu_core.object', {
#             'object': obj
#         })