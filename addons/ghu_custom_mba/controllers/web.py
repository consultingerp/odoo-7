# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.http import request


class GhuHome(Home):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        response = super(GhuHome, self).web_login(
            redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group(
                    'base.group_user'):
                redirect = b'/web?' + request.httprequest.query_string
            else:
                if not redirect and request.env.user.partner_id.is_student:
                    student = request.env['ghu.student'].sudo().search(
                    [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
                    if not student.vita_file_filename or not student.id_file_filename:
                        redirect='/campus/my/documents'
                    else:
                        redirect='/campus/courses'
                else:
                    redirect '/campus/documents' 
            return http.redirect_with_hash(redirect)
        return response
    
    #@http.route()
    #def index(self, *args, **kw):
    #    if request.session.uid and request.env.user.partner_id.is_custom_mba:
    #        return http.local_redirect('/campus/manage/courses', query=request.params, keep_hash=True)
    #    return super(Home, self).index(*args, **kw)
