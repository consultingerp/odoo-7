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
    
    @api.multi
    def createPanoptoFolder(self):
        for record in self:
            panopto = GhuPanopto(self.env)
            panoptoFolder = panopto.createFolder(record.name, "advisor"+str(record.id))
            user = self.env['res.users'].search([('partner_id','=',record.partner_id.id)], limit=1)
            panoptoUserId = panopto.getUserId(user)
            panopto.grantAccessToFolder(panoptoFolder, panoptoUserId, 'Creator')
            record.write({'panoptoFolder': panoptoFolder})