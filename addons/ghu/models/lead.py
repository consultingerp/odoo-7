from odoo import fields, models

class Lead(models.Model):
    _inherit = 'crm.lead'
    study_id = fields.Many2one(
        'ghu.study', 'Study', required=False)