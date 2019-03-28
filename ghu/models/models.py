# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ghu(models.Model):
    _name = 'ghu.student'
    _description = "Student"
    _inherits = {"res.partner": "partner_id"}

    student = fields.Boolean("Is student?")
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
