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
        partner = request.env.user.partner_id
        
        values = self._prepare_portal_layout_values()
        
        if partner.is_advisor or request.env.user.has_group('base.group_user'):
            folder_id = int(request.env['ir.config_parameter'].sudo().get_param('ghu.documents_advisor'))
            folder = request.env['documents.folder'].sudo().browse(folder_id)
            values['advisor_documents'] = folder.attachment_ids
            for attachment in values['advisor_documents']:
                attachment.generate_access_token()
        if partner.is_custom_mba or request.env.user.has_group('base.group_user'):
            folder_id = int(request.env['ir.config_parameter'].sudo().get_param('ghu.documents_custom_mba'))
            folder = request.env['documents.folder'].sudo().browse(folder_id)
            values['custom_mba_documents'] = folder.attachment_ids
            for attachment in values['custom_mba_documents']:
                attachment.generate_access_token()
        
        return request.render('ghu_custom_mba.campus_documents', values)
        