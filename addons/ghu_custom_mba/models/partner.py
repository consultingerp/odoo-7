# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class GhuPartner(models.Model):
    _inherit = 'res.partner'

    is_advisor = fields.Boolean(
        string=u'Is advisor?',
        compute='_is_advisor'
    )

    is_custom_mba = fields.Boolean(
        string=u'Is custom MBA?',
        compute='_is_custom_mba'
    )

    def _is_advisor(self):
        for record in self:
            if self.env['ghu.advisor'].sudo().search([('partner_id', '=', record.id)]):
                record.is_advisor = True
            else:
                record.is_advisor = False

    def _is_custom_mba(self):
        for record in self:
            if record.is_advisor:
                advisor = self.env['ghu.advisor'].sudo().search(
                    [('partner_id', '=', record.id)], limit=1)
                if advisor.is_cafeteria:
                    record.is_custom_mba = True
                else:
                    record.is_custom_mba = False
