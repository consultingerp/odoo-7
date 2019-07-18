import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ghu_documents_advisor = fields.Many2one(
        'documents.folder',
        string=u'General Information for advisor folders',
        config_parameter='ghu.documents_advisor',
    )

    ghu_documents_custom_mba = fields.Many2one(
        'documents.folder',
        string='General Information for custom MBA lecturers',
        config_parameter='ghu.documents_custom_mba'
    )