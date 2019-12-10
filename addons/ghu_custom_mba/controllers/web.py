# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.http import request


class Home(Home):

    #@http.route()
    #def index(self, *args, **kw):
    #    if request.session.uid and request.env.user.partner_id.is_custom_mba:
    #        return http.local_redirect('/campus/manage/courses', query=request.params, keep_hash=True)
    #    return super(Home, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        if not redirect and request.env.user.partner_id.is_custom_mba:
            return '/campus/manage/courses'
        if not redirect and request.env.user.partner_id.is_student:
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
            if not student.vita_file_filename or not student.id_file_filename:
                return '/campus/my/documents'
        return super(Home, self)._login_redirect(uid, redirect=redirect)