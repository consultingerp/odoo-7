from odoo import _, api, fields, models

class PaymentAcquirerAuthorize(models.Model):
    _inherit = 'payment.acquirer'

    def _get_authorize_urls(self, environment):
        """ Authorize URLs """
        if environment == 'prod':
            return {'authorize_form_url': 'https://cxpay.transactiongateway.com/gateway/transact.dll'}
        else:
            return {'authorize_form_url': 'https://cxpay.transactiongateway.com/gateway/transact.dll'}