# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class GhuStudent(models.Model):
    _inherit = 'ghu.student'
    
    custom_mba = fields.Boolean(
        string=u'custom MBA',
    )
    @api.multi
    def applicationReceived(self):
        notification_template = self.env.ref('ghu_custom_mba.application_received').sudo()
        for record in self:
            notification_template.send_mail(record.id, raise_exception=False, force_send=False)
            return True
    
    @api.multi
    def applicationApproved(self):
        notification_template = self.env.ref('ghu_custom_mba.application_approved').sudo()
        for record in self:
            notification_template.send_mail(record.id, raise_exception=False, force_send=False)
            return True