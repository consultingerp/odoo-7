# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models

class CampusMenu(models.Model):
    _inherit = 'website.menu'

    
    icon = fields.Char(
        string='Icon',
    )
    