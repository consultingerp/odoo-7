# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GhuAdvisor(models.Model):
    _name = 'ghu.advisor'
    _description = "Student"
    _inherits = {"res.partner": "partner_id"}

    @api.onchange('user_id')
    def onchange_user(self):
        if self.user_id:
            self.user_id.partner_id.supplier = True
            self.work_email = self.user_id.email
            self.identification_id = False