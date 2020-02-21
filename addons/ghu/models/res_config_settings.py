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

    def _default_ghu_automated_invoice_bank_account(self):
        return self.env['res.partner.bank'].search([])[0]

    ghu_automated_invoice_bank_account = fields.Many2one(
        'res.partner.bank',
        string='Automated Invoice Partner Bank',
        required=True,
        default=_default_ghu_automated_invoice_bank_account,
        config_parameter='ghu.automated_invoice_bank_account'
    )

    social_researchgate = fields.Char(related='website_id.social_researchgate', readonly=False)

    require_login = fields.Char(related='website_id.require_login', readonly=False)

    ghu_smarthub_api_key = fields.Char(
        string='Smarthub API Key',
        help='The Smarthub API key is needed to automatically import incoming leads.',
        required=True,
        default='1234',
        config_parameter='ghu.smarthub_api_key',
    )

    # @api.depends('website_id', 'social_twitter', 'social_facebook', 'social_github', 'social_linkedin', 'social_youtube', 'social_googleplus', 'social_instagram', 'social_researchgate')
    # def has_social_network(self):
    #     self.has_social_network = self.social_twitter or self.social_facebook or self.social_github \
    #         or self.social_linkedin or self.social_youtube or self.social_googleplus or self.social_instagram or self.social_researchgate

    # def inverse_has_social_network(self):
    #     if not self.has_social_network:
    #         self.social_twitter = ''
    #         self.social_facebook = ''
    #         self.social_github = ''
    #         self.social_linkedin = ''
    #         self.social_youtube = ''
    #         self.social_googleplus = ''
    #         self.social_instagram = ''
    #         self.social_researchgate = ''



    @api.model
    def get_values(self):
        return super(ResConfigSettings, self).get_values()

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
