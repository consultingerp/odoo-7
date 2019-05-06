import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_ghu_doctoral_application_fee_product(self):
        return self.env.ref('ghu.ghu_doctoral_application_fee').id
    
    ghu_doctoral_application_fee_product = fields.Many2one(
        'product.product',
        string='Doctoral Application Fee Product',
        help='This is the initial application fee product for the automated invoice.',
        required=True,
        default=_default_ghu_doctoral_application_fee_product,
        config_parameter='ghu.doctoral_application_fee_product',
    )

    ghu_transferwise_api_key = fields.Char(
        string='Transferwise API Key',
        help='The Transferwise API key is needed to automatically handle incoming payments.',
        required=True,
        default='1234',
        config_parameter='ghu.transferwise_api_key',
    )

    @api.model
    def get_values(self):
        return super(ResConfigSettings, self).get_values()

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
