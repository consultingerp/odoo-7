# -*- coding: utf-8 -*-
import json
import logging
import requests

_logger = logging.getLogger(__name__)


TRANSFERWISE_API_URL_SANDBOX = 'https://api.sandbox.transferwise.tech'
TRANSFERWISE_API_URL_LIVE = 'https://api.transferwise.com'

class Transferwise():
    def __init__(self, token, use_sandbox=False):
        self.token = token
        self.api_url = TRANSFERWISE_API_URL_SANDBOX if use_sandbox else TRANSFERWISE_API_URL_LIVE

    def _add_authorization(self, headers={}):
        return dict(**headers, Authorization='Bearer %s' % self.token)

    def _get_profiles(self):
        profiles = requests.get(
            '%s/v1/profiles' % self.api_url,
            headers=self._add_authorization()).json()
        if 'error' in profiles:
            _logger.error('Unable to fetch profiles: %r' % profiles)
            raise Exception('Unable to fetch profiles: %r' % profiles)
        return [p for p in profiles if p['type'] == 'business']

    def _get_accounts(self, profile_id):
        return requests.get(
            '%s/v1/borderless-accounts?profileId=%s' % (self.api_url, profile_id),
            headers=self._add_authorization()).json()

    def _get_statement(self, account_id, from_time, to_time, currency):
        statement = requests.get(
            '%s/v1/borderless-accounts/%s/statement.json?intervalStart=%sZ&intervalEnd=%sZ&currency=%s' % (self.api_url, account_id, from_time.isoformat(), to_time.isoformat(), currency),
            headers=self._add_authorization()).json()
        
        if 'error' in statement:
            _logger.error('Unable to fetch statement: %r, Error: %r' % ((account_id, from_time, to_time, currency), statement))
            return {}

        return statement

    def get_all_accounts(self):
        accounts = []
        for profile in self._get_profiles():
            # print("profile: %r" % profile)
            for account in self._get_accounts(profile['id']):
                # print("account: %r" % account)
                if account['active']:
                    currencies = []
                    for balance in account['balances']:
                        bank_details = balance.get('bankDetails') or {}
                        if bank_details.get('accountNumber'):
                            currencies.append({
                                'currency': balance['currency'],
                                'name': '%s, %s' % (bank_details.get('bankName'), bank_details.get('accountHolderName')),
                                'account_number': bank_details.get('accountNumber'),
                                'amount': balance['amount']['value'],
                            })
                    accounts.append({
                        'id': account['id'],
                        'currencies': currencies
                    })
        return accounts


    def get_statement_from_to(self, account_id, from_time, to_time, currency):
        '''returns statement in the time interval'''

        statement = self._get_statement(account_id, from_time, to_time, currency)

        transactions = []
        for t in statement['transactions']:
            transactions.append({
                'online_identifier': t['referenceNumber'],
                'date': t['date'],
                'name': t['details']['description'],
                'amount': t['amount']['value'],
                'end_amount': t['runningBalance']['value'],
                'meta': {
                    'sender_name': t['details'].get('senderName'),
                    'sender_account': t['details'].get('senderAccount'),
                    'payment_reference': t['details'].get('paymentReference'),
                },
            })

        return {
            'transactions': transactions,
            'balance': statement['endOfStatementBalance']['value'],
        }
