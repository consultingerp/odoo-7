import odoo

from odoo import http, models, fields, _
from odoo.http import request
from odoo.tools import pycompat, OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, _guess_mimetype
from odoo.addons.web.controllers.main import Binary
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.web import Home

class Campus(Home):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        homepage = request.website.homepage_id
        if homepage and (homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/' and homepage.sudo().require_login:
            return request.redirect('/web/login')

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