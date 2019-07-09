# -*- coding: utf-8 -*-
import requests
import json
import datetime
import logging

from odoo import models, api, fields
from odoo.tools.translate import _

from ..helpers.transferwise import Transferwise

_logger = logging.getLogger(__name__)

class TransferwiseProviderAccount(models.Model):
    _inherit = ['account.online.provider']

    provider_type = fields.Selection(selection_add=[('transferwise', 'Transferwise')])
    transferwise_sandbox_mode = fields.Boolean('Transferwise Sandbox Mode')
    transferwise_api_key = fields.Char('Transferwise API Key', size=64)

    @api.multi
    def _get_available_providers(self):
        ret = super(TransferwiseProviderAccount, self)._get_available_providers()
        ret.append('transferwise')
        return ret

    @api.multi
    def _get_favorite_institutions(self, country):
        resp_json = super(TransferwiseProviderAccount, self)._get_favorite_institutions(country)
        
        # inject transferwise provider (unfortunately no other way to do this)
        resp_json['result'].append({
            'provider': 'transferwise',
            'login_url': None,
            'country': None,
            'name': 'Transferwise GHU Custom',
            'beta': False,
            'picture': None,
            'institution_identifier': 'custom',
            'site_url': None,
        })

        return resp_json

    @api.multi
    def get_login_form(self, site_id, provider, beta=False):
        if provider != 'transferwise':
            return super(TransferwiseProviderAccount, self).get_login_form(site_id, provider, beta)
        
        view_id = self.env.ref('account_transferwise.transferwise_settings_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configure Transferwise Synchronization'),
            'res_model': 'account.online.provider',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[view_id, 'form']],
            'target': 'new',
            'context': {
                'default_transferwise_sandbox_mode': False,
            },
        }

    @api.model
    def create(self, vals):
        if 'transferwise_api_key' not in vals:
            return super(TransferwiseProviderAccount, self).create(vals)

        vals['provider_type'] = 'transferwise'
        vals['provider_identifier'] = 'custom'
        vals['status'] = 'SUCCESS'
        vals['status_code'] = 0

        tw = Transferwise(vals['transferwise_api_key'], use_sandbox=vals['transferwise_sandbox_mode'])
        accounts = tw.get_all_accounts()

        account_vals = []
        for account in accounts:
            for currency in account['currencies']:
                account_vals.append((0, 0, {
                    'name': currency['name'],
                    'account_number': currency['account_number'],
                    'online_identifier': '%s|%s' % (account['id'], currency['currency']),
                    'balance': currency['amount'],
                }))
        vals['account_online_journal_ids'] = account_vals
        
        return super(TransferwiseProviderAccount, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.provider_type != 'transferwise':
            return super(TransferwiseProviderAccount, self).write(vals)

        transferwise_api_key = vals['transferwise_api_key'] if 'transferwise_api_key' in vals else self.transferwise_api_key
        transferwise_sandbox_mode = vals['transferwise_sandbox_mode'] if 'transferwise_sandbox_mode' in vals else self.transferwise_sandbox_mode

        vals['provider_type'] = 'transferwise'
        vals['provider_identifier'] = 'custom'
        vals['status'] = 'SUCCESS'
        vals['status_code'] = 0

        tw = Transferwise(transferwise_api_key, use_sandbox=transferwise_sandbox_mode)
        accounts = tw.get_all_accounts()

        account_vals = []
        for account in accounts:
            for currency in account['currencies']:
                action = 0
                journal_id = 0
                online_identifier = '%s|%s' % (account['id'], currency['currency'])
                for existing_journal in self.account_online_journal_ids:
                    if existing_journal.online_identifier == online_identifier:
                        action = 1
                        journal_id = existing_journal.id

                account_vals.append((action, journal_id, {
                    'name': currency['name'],
                    'account_number': currency['account_number'],
                    'online_identifier': online_identifier,
                    'balance': currency['amount'],
                }))

        # find old journals that need to be deleted
        for existing_journal in self.account_online_journal_ids:
            # check if the journal is somehow on the list to be added or updated, if not -> delete
            if existing_journal.id not in [v[1] for v in account_vals if v[0] > 0]:
                account_vals.append((2, existing_journal.id))

        vals['account_online_journal_ids'] = account_vals
        
        return super(TransferwiseProviderAccount, self).write(vals)

    @api.multi
    def manual_sync(self):
        if self.provider_type != 'transferwise':
            return super(TransferwiseProviderAccount, self).manual_sync()
        transactions = []
        for account in self.account_online_journal_ids:
            if account.journal_ids:
                tr = account.retrieve_transactions()
                transactions.append({'journal': account.journal_ids[0].name, 'count': tr})
        
        result = {'status': 'SUCCESS', 'transactions': transactions, 'method': 'refresh', 'added': self.env['account.online.journal']}
        
        return self.show_result(result)

    @api.multi
    def update_credentials(self):
        # maybe we should just trigger a manual refresh here as well (or tell the user to update the api key in the form)
        return None

    @api.model
    def cron_fetch_online_transactions(self):
        if self.provider_type != 'transferwise':
            return super(TransferwiseProviderAccount, self).cron_fetch_online_transactions()
        self.manual_sync()

class TransferwiseAccount(models.Model):
    _inherit = 'account.online.journal'

    @api.multi
    def retrieve_transactions(self):
        if (self.account_online_provider_id.provider_type != 'transferwise'):
            return super(TransferwiseAccount, self).retrieve_transactions()
        
        tw = Transferwise(self.account_online_provider_id.transferwise_api_key, use_sandbox=self.account_online_provider_id.transferwise_sandbox_mode)

        account_id, currency = self.online_identifier.split('|')
        statement = tw.get_statement_from_to(account_id, datetime.datetime.fromordinal((datetime.date(year=2019, month=5, day=1)).toordinal()), datetime.datetime.fromordinal(fields.Date.today().toordinal()), currency)

        transactions = []

        # Prepare the transaction
        for transaction in statement['transactions']:
            trans = {
                'online_identifier': transaction['online_identifier'],
                'date': fields.Date.from_string(transaction['date']),
                'name': transaction['name'],
                'amount': transaction['amount'],
                'account_number': transaction['meta']['sender_account'],
                'end_amount': statement['balance'],
            }
            if transaction['meta'].get('payment_reference') and transaction['amount'] > 0:
                trans['online_partner_vendor_name'] = transaction['meta']['sender_name']
                trans['partner_id'] = self._find_partner([('online_partner_vendor_name', '=', transaction['meta']['sender_name'])])
            # if 'location' in transaction and not trans.get('partner_id'):
            #     trans['partner_id'] = self._find_partner_from_location(transaction.get('location'))
            transactions.append(trans)

        # Create the bank statement with the transactions
        return self.env['account.bank.statement'].online_sync_bank_statement(transactions, self.journal_ids[0])
