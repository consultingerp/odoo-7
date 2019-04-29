from odoo import fields, models

class Lead(models.Model):
    _inherit = 'crm.lead'
    study_id = fields.Many2one(
        'ghu.study', 'Study', required=False)
        
    nationality = fields.Many2one(
        string=u'Nationality',
        comodel_name='res.country',
        required=False)

    highest_degree = fields.Char(
        string=u'Highest Degree',
    )
    