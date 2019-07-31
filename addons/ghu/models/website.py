import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _default_social_researchgate(self):
        return self.env.ref('base.main_company').social_researchgate

    social_researchgate = fields.Char('Researchgate Account', default=_default_social_researchgate)