# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
import base64
import werkzeug

_logger = logging.getLogger(__name__)

class GhuCustomMba(http.Controller):
    @http.route('/campus/course/', auth='user')
    def index(self, **kw):
        return "Hello, world"

    #@http.route('/campus/courses/', auth='user', website=True)
    #def list(self, **kw):
    #    return http.request.render('ghu_custom_mba.courselist', {
    #        'root': '/campus/course',
    #        'objects': http.request.env['ghu_custom_mba.course'].search([]),
    #    })

    @http.route('/campus/my/courses/', auth='user', website=True)
    def listMyCourses(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            partner_id = request.env.user.partner_id
            advisor = request.env['ghu.advisor'].sudo().search([('partner_id','=',partner_id)], limit=1)
            advisor_id = advisor.id
        else:
            return http.request.not_found()
        return http.request.render('ghu_custom_mba.courselist', {
            'root': '/campus/course',
            'author': 'true',
            'objects': http.request.env['ghu_custom_mba.course'].search([('author_id','=',advisor_id)]),
        })

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/', auth='user', website=True)
    def detail(self, obj, **kw):
        _logger.info(request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])[0].partner_id.id)
        return http.request.render('ghu_custom_mba.coursedetail', {
            'root': '/campus/course',
            'object': obj,
            'author': 'true',
        })

    @http.route('/campus/course/new', methods=['GET'], auth='user', website=True)
    def new(self, **kw):
        course_model = request.env['ir.model'].sudo().search([('model', '=', 'ghu_custom_mba.course')])
        course_fields = request.env['ir.model.fields'].sudo().search([
            ('model_id', '=', course_model.id),
        ])
        all_fields = dict()
        for f in course_fields:
            all_fields[f['name']] = ''
        languages = request.env['ghu.lang'].sudo().search([('name','!=','')])
        programs = request.env['ghu.program'].sudo().search([])
        return http.request.render('ghu_custom_mba.courseedit', {
            'root': '/campus/course',
            'new': True,
            'object': all_fields,
            'languages': languages,
            'programs': programs,
        })

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/edit', methods=['GET'], auth='user', website=True)
    def edit(self, obj, **kw):
        languages = request.env['ghu.lang'].sudo().search([('name','!=','')])
        programs = request.env['ghu.program'].sudo().search([])
        return http.request.render('ghu_custom_mba.courseedit', {
            'root': '/campus/course',
            'object': obj,
            'author': 'true',
            'languages': languages,
            'programs': programs,
        })

    @http.route('/campus/course/save/', methods=['POST'], auth='user', website=True)
    def create(self, **kw):
        partner_id = request.env['res.users'].sudo().search([('id', '=', http.request.env.context.get('uid'))])[0].partner_id.id
        advisor_id = request.env['ghu.advisor'].sudo().search([('partner_id','=',partner_id)])[0].id
        kw['author_id'] = advisor_id
        kw['status'] = 'draft'
        for key in list(kw.keys()):
            if hasattr(kw[key], 'filename'):
                value = kw.pop(key)
                kw[(key + '_filename')] = value.filename
                kw[key] = base64.b64encode(value.read())
        course_record = request.env['ghu_custom_mba.course'].with_context(mail_create_nosubscribe=True).create(kw)
        return werkzeug.utils.redirect('/campus/course/'+str(course_record.id))

    @http.route('/campus/course/save/<model("ghu_custom_mba.course"):obj>', methods=['POST'], auth='user', website=True)
    def update(self, obj, **kw):
        for key in list(kw.keys()):
            if hasattr(kw[key], 'filename'):
                value = kw.pop(key)
                kw[(key + '_filename')] = value.filename
                kw[key] = base64.b64encode(value.read())
        kw['status'] = 'draft'
        for key in list(kw.keys()):
            if not kw[key]:
                del kw[key]
        obj.write(kw)
        return werkzeug.utils.redirect('/campus/course/'+str(obj.id))

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/review', methods=['GET'], auth='user', website=True)
    def review(self, obj, **kw):
        kw = dict()
        kw['state'] = 'new'
        obj.write(kw)
        return werkzeug.utils.redirect('/campus/my/courses')