# -*- coding: utf-8 -*-


import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class GhuEnrollment(models.AbstractModel):
    _name = 'ghu.enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GHU Enrollment'

    study_ref = fields.Reference(
        string='Study',
        selection=[('ghu.study', 'Study')]
    )

    student_ref = fields.Reference(
        string=u'Student',
        selection=[('ghu.student', 'Student')]
    )

    invoice_ref = fields.Reference(
        string=u'Invoice',
        selection=[('account.invoice', 'Invoice')]
    )