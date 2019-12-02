from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from ..util.panopto import GhuPanopto
import logging
import datetime

_logger = logging.getLogger(__name__)


class GhuCourseEnrollment(models.Model):
    _name = 'ghu_custom_mba.course_enrollment'
    _rec_name = 'name'
    _description = "Course Enrollment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
        ('completed', 'Completed'),
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

    examination_ids = fields.One2many(
        string=u'Examinations',
        comodel_name='ghu_custom_mba.examination',
        inverse_name='enrollment_id',
        limit=2
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
        user = self.env['res.users'].search(
            [('partner_id', '=', self.student_ref.partner_id.id)], limit=1)
        panoptoUserId = panopto.getUserId(user)
        panopto.grantAccessToSession(
            self.course_ref.lecture1_video_id, panoptoUserId)
        panopto.grantAccessToSession(
            self.course_ref.lecture2_video_id, panoptoUserId)
        panopto.grantAccessToSession(
            self.course_ref.lecture3_video_id, panoptoUserId)


class GhuExamination(models.Model):
    _name = 'ghu_custom_mba.examination'
    _rec_name = 'name'
    _description = "Examination"

    enrollment_id = fields.Many2one(
        string=u'Enrollment',
        comodel_name='ghu_custom_mba.course_enrollment',
        ondelete='cascade',
    )

    name = fields.Char('Name', compute='_compute_name')

    @api.depends('type', 'request_date')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.request_date.strftime("%b %d %Y")

    type = fields.Char('Type', size=128, required=True)

    question_title = fields.Char('Question Title', required=True)

    question = fields.Html('Question', required=True)

    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
    )


    end_date = fields.Date(
        string='End Date',
        compute='_compute_enddate'
    )
    @api.depends('request_date')
    def _compute_enddate(self):
        for rec in self:
            rec.name = rec.request_date + datetime.timedelta(days=21)


    submission = fields.Binary(string='Submission', attachment=True)

    # Grading section

    grade = fields.Float(
        string='Grade',
        digits=(3, 1)
    )

    # 44 to 50 Points = Excellent (1)
    # 38 to 43 Points = Good (2)
    # 32 to 37 Points = Satisfactory (3)
    # 26 to 31 Points = Pass (4)
    # below 25 = Fail (5)
    @api.one
    @api.constrains('grade')
    def _check_grade(self):
        if self.grade > 50.0 or self.grade < 0.0:
            raise ValidationError(
                "Grading score must be between 0 and 50 points.")

    result = fields.Html(
        string='Comment on grading',
    )
