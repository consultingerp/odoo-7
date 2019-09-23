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
        notification_template = self.env.ref(
            'ghu_custom_mba.application_received').sudo()
        for record in self:
            notification_template.send_mail(
                record.id, raise_exception=False, force_send=False)
            return True

    @api.multi
    def applicationApproved(self):
        notification_template = self.env.ref(
            'ghu_custom_mba.application_approved').sudo()
        for record in self:
            notification_template.send_mail(
                record.id, raise_exception=False, force_send=False)
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
            notification_template.send_mail(
                record.id, raise_exception=False, force_send=False)
            return True
