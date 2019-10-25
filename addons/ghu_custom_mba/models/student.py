# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
import base64

_logger = logging.getLogger(__name__)


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
        notification_template = self.env.ref(
            'ghu_custom_mba.application_approved').sudo()
        for record in self:
            record.partner_id.message_post_with_template(template_id=notification_template.id)
            return True

    @api.multi
    def studentEnrolled(self):
        for record in self:
            pdf = self.env.ref('ghu.enrolment_confirmation_pdf').sudo(
            ).render_qweb_pdf([record.id])[0]
            attachmentName = 'Enrolment-'+record.lastname + \
                '-'+record.student_identification+'.pdf'
            attachment = self.env['ir.attachment'].create({
                'name': attachmentName,
                'type': 'binary',
                'datas': base64.encodestring(pdf),
                'datas_fname': attachmentName,
                'res_model': 'ghu.student',
                'res_id': record.id,
                'mimetype': 'application/x-pdf'
            })
            notification_template = self.env.ref(
                'ghu_custom_mba.student_enrolled').sudo()
            notification_template.attachment_ids = False
            notification_template.attachment_ids = [(4, attachment.id)]
            
            record.partner_id.message_post_with_template(template_id=notification_template.id)
            return True
