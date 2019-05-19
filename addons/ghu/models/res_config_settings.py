import logging

from odoo import api, fields, models

from ..helpers.transferwise import Transferwise

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

    def _get_transferwise_borderless_accounts(self):
        tw = Transferwise(self.env['ir.config_parameter'].get_param('ghu.transferwise_api_key'))
        accounts = tw.get_all_accounts()
        res = []
        if accounts:
            for account in accounts:
                for currency in account['currencies']:
                    res.append((
                        '%s/%s' % (account['id'], currency['currency']),
                        '%s (%s) in %s at %s' % (
                            currency['bankDetails']['accountHolderName'], 
                            currency['bankDetails']['accountNumber'], 
                            currency['bankDetails']['currency'], 
                            currency['bankDetails']['bankName'],
                        )
                    ))
        res.append(('invalid', 'Invalid Account, please check Transferwise API key'))
        return res

    def _default_ghu_transferwise_borderless_account(self):
        accounts = self._get_transferwise_borderless_accounts()
        return accounts[0][0]

    ghu_transferwise_borderless_account = fields.Selection(
        _get_transferwise_borderless_accounts,
        string='Transferwise Borderless Account',
        help='The Transferwise borderless bank account which is used to receive money.',
        required=True,
        default=_default_ghu_transferwise_borderless_account,
        config_parameter='ghu.transferwise_borderless_account'
    )

    def _default_ghu_automated_invoice_bank_journal(self):
        return self.env['account.journal'].search([('type', '=', 'bank')])[0]

    ghu_automated_invoice_bank_journal = fields.Many2one(
        'account.journal',
        string='Automated Invoice Bank Journal',
        required=True,
        default=_default_ghu_automated_invoice_bank_journal,
        config_parameter='ghu.automated_invoice_bank_journal'
    )

    @api.model
    def get_values(self):
        return super(ResConfigSettings, self).get_values()

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
