# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import base64
from odoo.tools import email_split

_logger = logging.getLogger(__name__)


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class GhuStudent(models.Model):
    _inherit = 'ghu.student'

    custom_mba = fields.Boolean(
        string=u'custom MBA',
    )

    @api.multi
    def applicationReceived(self):
        notification_template_en = self.env.ref(
            'ghu_custom_mba.application_received_en').sudo()
        notification_template_es = self.env.ref(
            'ghu_custom_mba.application_received_es').sudo()
        for record in self:
            if record.native_language.name == 'Spanish':
                record.partner_id.message_post_with_template(template_id=notification_template_es.id)
            else:
                record.partner_id.message_post_with_template(template_id=notification_template_en.id)
        return True

    @api.multi
    def applicationApproved(self):
        self_sudo = self.sudo()
        notification_template = self_sudo.env.ref(
            'ghu_custom_mba.application_approved').sudo()
        for record in self_sudo:
            pdf = self_sudo.env.ref('ghu.enrollment_confirmation_pdf').sudo(
            ).render_qweb_pdf([record.id])[0]
            attachmentName = 'Enrollment-' + record.lastname + \
                             '-' + record.student_identification + '.pdf'
            attachment = self_sudo.env['ir.attachment'].create({
                'name': attachmentName,
                'type': 'binary',
                'datas': base64.encodestring(pdf),
                'datas_fname': attachmentName,
                'res_model': 'ghu.student',
                'res_id': record.id,
                'mimetype': 'application/x-pdf'
            })
            notification_template.attachment_ids = False
            notification_template.attachment_ids = [(4, attachment.id)]
            # Create Portal Access for student if there is no one yet
            user = record.partner_id.user_ids[0] if record.partner_id.user_ids else None
            if not user:
                user = self_sudo.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
                    'email': extract_email(record.partner_id.email),
                    'login': extract_email(record.partner_id.email),
                    'partner_id': record.partner_id.id,
                    'company_id': 1,
                    'company_ids': [(6, 0, [1])],
                })
                partner = record.partner_id
                lang = user.lang
                portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                    partner.id]
                partner.signup_prepare()
            lang = user.lang
            record.partner_id.message_post_with_template(
                template_id=notification_template.with_context(dbname=self_sudo._cr.dbname, lang=lang).id)
        return True

    def get_enrollment_pdf(self):
        self.ensure_one()
        self_sudo = self.sudo(self.env().user)
        pdf = self_sudo.env.ref('ghu.enrollment_confirmation_pdf').sudo(
        ).render_qweb_pdf([self.id])[0]
        attachmentName = 'Enrollment-' + self.lastname + \
                         '-' + self.student_identification + '.pdf'
        attachment = self_sudo.env['ir.attachment'].create({
            'name': attachmentName,
            'type': 'binary',
            'datas': base64.encodestring(pdf),
            'datas_fname': attachmentName,
            'res_model': 'ghu.student',
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        return attachment.id
