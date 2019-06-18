# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)

class GhuCampus(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(GhuCampus, self)._prepare_portal_layout_values()
        return values

    @http.route('/campus/documents/', type='http', auth='user', methods=['GET'], website=True)
    def show_document_list(self, **kwargs):
        user = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        advisor = False
        if request.env['ghu.advisor'].sudo().search([('partner_id', '=', user.id)]):
            advisor = True
        if advisor:
            folder_id = int(request.env['ir.config_parameter'].sudo().get_param('ghu.documents_advisor_general'))
            folder = request.env['documents.folder'].sudo().browse(4)
            values['documents'] = folder.attachment_ids
            for attachment in values['documents']:
                attachment.generate_access_token()
            
        
        return request.render('ghu.campus_documents', values)
        