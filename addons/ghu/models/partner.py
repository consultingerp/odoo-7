# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GhuPartner(models.Model):
    _inherit = 'res.partner'

    interest_id = fields.Many2many('ghu.partner.interest', relation='ghu_partner_interest', column1='partner_id',
                                   column2='interest_id', string='Tags')
