from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from ..util.panopto import GhuPanopto
import logging

_logger = logging.getLogger(__name__)


class GhuCourseEnrollment(models.Model):
    _name = 'ghu_custom_mba.course_enrollment'
    _rec_name = 'name'
    _description = "Course Enrollment"

    name = fields.Char(
        string=u'Name',
    )
    
    invoice_ref = fields.Reference(
        string=u'Invoice',
        selection=[('account.invoice', 'Invoice')]
    )

    course_ref = fields.Reference(
        string=u'Course',
        selection=[('ghu_custom_mba.course', 'Course')]
    )

    student_ref = fields.Reference(
        string=u'Student',
        selection=[('ghu.student', 'Student')]
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


    @api.multi
    def write(self, values):
        if 'state' in values:
            self.on_state_change(values['state'])
        super(GhuCourseEnrollment, self).write(values)


    def on_state_change(self, new_state):
        # generate invoice
        if new_state == 'paid':
            if self.state == 'new':
                self.enrollmentFinished()  # Send mail to advisor to review

    def enrollmentFinished(self):
        # Find all 3 lectures and add ids to model
        panopto = GhuPanopto(self.env)
        user = self.env['res.users'].search([('partner_id','=',self.student_ref.partner_id.id)], limit=1)
        panoptoUserId = panopto.getUserId(user)
        panopto.grantAccessToFolder(self.course_ref.panopto_id, panoptoUserId, 'Viewer')