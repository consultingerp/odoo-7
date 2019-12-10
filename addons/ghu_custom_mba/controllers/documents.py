# -*- coding: utf-8 -*-
import logging
import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import werkzeug
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
        if partner.is_custom_mba_student or request.env.user.has_group('base.group_user'):
            folder_id = int(request.env['ir.config_parameter'].sudo().get_param('ghu.documents_student_custom_mba'))
            folder = request.env['documents.folder'].sudo().browse(folder_id)
            values['student_custom_mba_documents'] = folder.attachment_ids
            for attachment in values['student_custom_mba_documents']:
                attachment.generate_access_token()
        if partner.is_doctoral_student or request.env.user.has_group('base.group_user'):
            folder_id = int(request.env['ir.config_parameter'].sudo().get_param('ghu.documents_student_doctoral'))
            folder = request.env['documents.folder'].sudo().browse(folder_id)
            values['student_doctoral_documents'] = folder.attachment_ids
            for attachment in values['student_doctoral_documents']:
                attachment.generate_access_token()
        values['slug'] = 'campus_documents' 
        return request.render('ghu_custom_mba.campus_documents', values)
        

    @http.route('/campus/my/documents/', type='http', auth='user', methods=['GET'], website=True)
    def showDocuments(self, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            return http.request.render('ghu_custom_mba.campus_student_documents', {
                'root': '/campus/course',
                'student': student,
                'slug': 'campus_documents'
            })
    @http.route('/campus/my/documents/save', type='http', auth="user", methods=['POST'], website=True)
    def saveDocuments(self, **post):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            if post.get('cv',False) and post.get('id',False):
                cv_name = post.get('cv').filename      
                cv_file = post.get('cv')
                cv_attachment = cv_file.read() 
                id_name = post.get('id').filename      
                id_file = post.get('id')
                id_attachment = id_file.read() 
                student.sudo().write({
                    'vita_file': base64.b64encode(cv_attachment),
                    'vita_file_filename': cv_name,
                    'id_file': base64.b64encode(id_attachment),
                    'id_file_filename': id_name
                })
                return request.render('ghu_custom_mba.campus_student_documents_saved',{
                    'student': student
                })
        return werkzeug.utils.redirect('/campus/my/documents')