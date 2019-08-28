# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from ..util.panopto import GhuPanopto

_logger = logging.getLogger(__name__)


class GhuCustomMbaAdvisor(models.Model):
    _inherit = 'ghu.advisor'

    panoptoFolder = fields.Char(
        string=u'Panopto Folder',
    )

    videoCheck = fields.Boolean(
        string=u'Video Checked',
    )
    
    
    def createPanoptoFolder(self):
        panopto = GhuPanopto(self.env)
        panoptoFolder = panopto.createFolder(self.name, "advisor"+str(self.id))
        user = self.env['res.users'].search([('partner_id','=',self.partner_id.id)], limit=1)
        panoptoUserId = panopto.getUserId(user)
        panopto.grantAccessToFolder(panoptoFolder, panoptoUserId, 'Creator')
        self.write({'panoptoFolder': panoptoFolder})