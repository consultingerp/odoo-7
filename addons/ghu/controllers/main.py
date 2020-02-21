# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class GhuWebsite(Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        
        if request.website.sudo().require_login and request.env.user._is_public():
            return request.redirect('/web/login')
        
        homepage = request.website.homepage_id
        if homepage and (homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/':
            return request.env['ir.http'].reroute(homepage.url)

        website_page = request.env['ir.http']._serve_page()
        if website_page:
            return website_page
        else:
            top_menu = request.website.menu_id
            first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered(lambda menu: menu.is_visible)
            if first_menu and first_menu[0].url not in ('/', '', '#') and (not (first_menu[0].url.startswith(('/?', '/#', ' ')))):
                return request.redirect(first_menu[0].url)

        raise request.not_found()