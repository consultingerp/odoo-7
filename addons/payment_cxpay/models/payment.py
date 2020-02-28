from odoo import _, api, fields, models
from odoo.addons.payment_authorize.models.payment import PaymentAcquirerAuthorize

class PaymentAcquirerCXPay(PaymentAcquirerAuthorize):

    def _get_authorize_urls(self, environment):
        """ Authorize URLs """
        if environment == 'prod':
            return {'authorize_form_url': 'https://cxpay.transactiongateway.com/cart/ausi.php'}
        else:
            return {'authorize_form_url': 'https://cxpay.transactiongateway.com/cart/ausi.php'}