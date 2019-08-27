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

    ghu_panopto_user = fields.Char(
        string='Panopto Username',
        config_parameter='ghu.panopto_user'
    )

    ghu_panopto_password = fields.Char(
        string='Panopto Password',
        config_parameter='ghu.panopto_password'
    )

    ghu_panopto_server = fields.Char(
        string='Panopto Server',
        config_parameter='ghu.panopto_server'
    )

    ghu_panopto_blti_consumer_key = fields.Char(
        string='Panopto BLTI Consumer Key',
        config_parameter='ghu.panopto_blti_consumer_key'
    )

    ghu_panopto_blti_consumer_secret = fields.Char(
        string='Panopto BLTI Consumer Secret',
        config_parameter='ghu.panopto_blti_consumer_secret'
    )

    ghu_panopto_blti_launch_url = fields.Char(
        string='Panopto BLTI Launch URL',
        config_parameter='ghu.panopto_blti_launch_url'
    )