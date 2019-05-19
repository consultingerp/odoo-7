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
            return []
        return profiles

    def _get_accounts(self, profile_id):
        return requests.get(
            '%s/v1/borderless-accounts?profileId=%s' % (self.api_url, profile_id),
            headers=self._add_authorization()).json()

    def _get_statements(self, account_id, from_time, to_time, currency):
        return requests.get(
            '%s/v1/borderless-accounts/%s/statement.json?intervalStart=%sZ&intervalEnd=%sZ&currency=%s' % (self.api_url, account_id, from_time.isoformat(), to_time.isoformat(), currency),
            headers=self._add_authorization()).json()['transactions']

    def get_all_accounts(self):
        accounts = []
        for profile in self._get_profiles():
            for account in self._get_accounts(profile['id']):
                if account['active']:
                    currencies = []
                    for balance in account['balances']:
                        if balance.get('bankDetails'):
                            currencies.append({
                                'currency': balance['currency'],
                                'bankDetails': balance['bankDetails'],
                            })
                    accounts.append({
                        'id': account['id'],
                        'currencies': currencies
                    })
        return accounts


    def get_all_statements_from_to(self, account_id, from_time, to_time, currency):
        '''returns all statements in the time interval in the form of
        [{
            'amount': {'currency': 'USD', 'value': 3000000.0},
            'date': '2019-05-12T17:21:25.061Z',
            'details': {'description': 'No information', 'type': 'UNKNOWN'},
            'exchangeDetails': None,
            'referenceNumber': 'CARD-BNK-1234567',
            'runningBalance': {'currency': 'USD', 'value': 3000000.0},
            'totalFees': {'currency': 'USD', 'value': 0.0},
            'type': 'CREDIT'
        }]
        '''

        return self._get_statements(account_id, from_time, to_time, currency)
