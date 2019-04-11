# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GhuEmployee(models.Model):
 _inherit = 'hr.employee'
 # we inherited res.groups model which is Odoo/OpenERP built in model and created two fields in that model.
 _order = "website_order"

 skype = fields.Char(string="Skype")
 website_order = fields.Integer(string="Order")