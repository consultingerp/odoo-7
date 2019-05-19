import datetime
import json
import logging

from odoo import models, fields, api

from ..helpers.transferwise import Transferwise

_logger = logging.getLogger(__name__)

'''Extend account payment with transferwise fetch statements utility
'''
class AccountBankStatementTransferwise(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def fetch_transferwise_statements(self, since_hours=72):
        tw = Transferwise(self.env['ir.config_parameter'].get_param('ghu.transferwise_api_key'))
        now = datetime.datetime.utcnow()

        account_id, currency = self.env['ir.config_parameter'].get_param('ghu.transferwise_borderless_account').split('/')

        statements = tw.get_all_statements_from_to(account_id, now - datetime.timedelta(days=60), now, currency)

        for statement in statements:
            self._create_payment(statement)

    def _create_payment(self, statement):
        if len(self.search([('reference_number', '=', statement['referenceNumber'])])) > 0:
            _logger.info('Already handled payment with reference number %r' % statement['referenceNumber'])
            return

        payment = dict(
            ### from account.abstract.payment:
            payment_type = 'inbound' if statement['type'] == 'CREDIT' else 'outbound',
            payment_method_id = self.env.ref('account.account_payment_method_manual_in' if statement['type'] == 'CREDIT' else 'account.account_payment_method_manual_out').id,
            partner_type = 'customer',
            # partner_id = None?
            amount = abs(statement['amount']['value']),
            currency_id = self.env.ref('base.%s' % statement['amount']['currency']).id,
            payment_date = datetime.datetime.strptime(statement['date'], '%Y-%m-%dT%H:%M:%S.%fz').date(),
            communication = json.dumps(statement['details'], indent=2),
            journal_id = self.env['ir.config_parameter'].get_param('ghu.automated_invoice_bank_journal'),

            ### from account.payment
            payment_reference = statement['details'].get('paymentReference'),

            ### from ghu.account_transferwise_payment
            reference_number = statement['referenceNumber'],
        )

        self.create(payment)

class AccountBankStatementLineTransferwise(models.Model):
    _inherit = 'account.bank.statement.line'

    account_bank_statement_line_id = fields.Many2one('account.bank.statement.line', 'Account Bank Statement Line')
    transferwise_reference_number = fields.Char('Transferwise Reference Number', size=64)

    _sql_constraints = [
        ('transferwise_reference_number_unique', 'unique(journal_id, transferwise_reference_number)', 'This reference number already exists, please check this payment.'),
    ]
