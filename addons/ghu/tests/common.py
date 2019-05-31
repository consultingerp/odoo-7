# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestGhuCases(TransactionCase):

    def setUp(self):
        super(TestGhuCases, self).setUp()

        # Create a user as 'Crm Salesmanager' and added the `sales manager` group
        #self.crm_salemanager = self.env['res.users'].create({
        #    'company_id': self.env.ref("base.main_company").id,
        #    'name': "Crm Sales manager",
        #    'login': "csm",
        #    'email': "crmmanager@yourcompany.com",
        #    'groups_id': [(6, 0, [self.ref('sales_team.group_sale_manager')])]
        #})