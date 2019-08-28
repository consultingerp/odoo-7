# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from ..util.panopto import GhuPanopto

_logger = logging.getLogger(__name__)


class GhuCustomMbaAdvisor(models.Model):
    _inherit = 'ghu.advisor'

    def createPanoptoFolder(self):
        panopto = GhuPanopto(self.env)
        self.panoptoFolder = panopto.createFolder(self.name, "advisor"+str(self.id))
        user = self.env['res.users'].search([('partner_id','=',self.partner_id.id)], limit=1)
        panoptoUserId = panopto.getUserId(user)
        panopto.grantAccessToFolder(self.panoptoFolder, panoptoUserId, 'Creator')