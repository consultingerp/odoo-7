from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from ..util.panopto import GhuPanopto
import logging

_logger = logging.getLogger(__name__)


class GhuCourseEnrollment(models.Model):
    _name = 'ghu_custom_mba.course_enrollment'
    _rec_name = 'name'
    _description = "Course Enrollment"

    invoice_ref = fields.Reference(
        string=u'Invoice',
        selection=[('account.invoice', 'Invoice')]
    )

    course_ref = fields.Reference(
        string=u'Course',
        selection=[('ghu_custom_mba.course', 'Course')]
    )

    states = [
        ('new', 'New'),
        ('paid', 'Paid'),
        ('examination', 'Examination in Progress'),
        ('grading', 'Grading in Progress'),
        ('completed', 'Completed' ),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]

    # PROCESS FIELDS
    state = fields.Selection(
        states,
        'State', default='new', required=True, track_visibility='onchange', group_expand='_read_group_stage_ids'
    )

    examination_count = fields.Integer(
        string=u'Examination Count',
    )
    

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return [k for k, v in self.states]

