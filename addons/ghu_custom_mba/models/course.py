from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from ..util.panopto import GhuPanopto
import logging

_logger = logging.getLogger(__name__)


class GhuCourse(models.Model):
    _name = 'ghu_custom_mba.course'
    _rec_name = 'name'
    _description = "Course"

    name = fields.Char('Name', size=128, required=True)
    long_name = fields.Char('Long Name', size=256, required=True)
    description = fields.Html(
        string=u'Description',
    )

    aims = fields.Html(
        string=u'Aims',
    )

    # Learning Outcomes
    knowledge = fields.Html(
        string=u'Knowledge',
    )

    skills = fields.Html(
        string=u'Skills',
    )

    syllabus = fields.Html(
        string=u'Syllabus',
    )

    strategies = fields.Html(
        string=u'Learning, Teaching and Assessment Strategies',
    )

    assessment_ids = fields.One2many(
        string=u'Assessments',
        comodel_name='ghu_custom_mba.assessment',
        inverse_name='course_id',
    )

    shortcode = fields.Char('Short Code', size=256, required=False)

    language = fields.Many2one(
        string=u'Language',
        comodel_name='ghu.lang',
        required=True,
    )

    program_id = fields.Many2one(
        string=u'Program',
        comodel_name='ghu.program',
    )

    script_file = fields.Binary('Script', required=False)
    script_file_filename = fields.Char(
        string=u'Script Filename',
    )

    author_id = fields.Many2one(
        string=u'Author',
        comodel_name='ghu.advisor',
        domain=[('is_cafeteria', '=', 'True')],
    )

    product_ref = fields.Reference(
        string=u'Product',
        selection=[('product.product', 'Product')]
    )

    panopto_id = fields.Char('Panopto ID', size=256, required=False)

    preview_video_id = fields.Char(
        'Panopto Video Preview ID', size=256, required=False)

    lecture1_video_id = fields.Char(
        'Panopto Video Lecture 1 ID', size=256, required=False)

    lecture2_video_id = fields.Char(
        'Panopto Video Lecture 2 ID', size=256, required=False)

    lecture3_video_id = fields.Char(
        'Panopto Video Lecture 3 ID', size=256, required=False)

    creditpoints = fields.Char(
        'Creditpoints Description', size=256, required=False)

    assessment_ids = fields.One2many(
        string=u'Assessments',
        comodel_name='ghu_custom_mba.assessment',
        inverse_name='course_id',
        limit=2
    )

    # Workflow specifics
    formal_check_done = fields.Boolean(
        string=u'Formal check done?',
    )
    formal_check = fields.Boolean(
        string=u'Formal check result',
    )
    formal_reason = fields.Text(
        string=u'Formal check reason',
    )
    content_check_done = fields.Boolean(
        string=u'Content check done?',
    )
    content_check = fields.Boolean(
        string=u'Content check',
    )
    content_reason = fields.Text(
        string=u'Content check reason',
    )

    states = [
        ('draft', 'Draft'),  # Created by Lecturer but not finished configuration
        # Submitted by Lecturer but not finished formal and content check
        ('new', 'In Review'),
        # Script is fine and can be recorded
        ('script_approved', 'Recording in progress'),
        ('recording_finished', 'Recording In Review'),  # Recording is checked
        # Module is checked for content and formal, published
        ('approved', 'Approved'),
        ('declined', 'Declined'),  # Module is checked but didn't met requirements
        ('outdated', 'Outdated'),  # Module has to be revised
    ]

    # PROCESS FIELDS
    state = fields.Selection(
        states,
        'State', default='draft', required=True, track_visibility='onchange', group_expand='_read_group_stage_ids'
    )
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return [k for k, v in self.states]

    required_review_fields = [
        'name',
        'aims',
        'knowledge',
        'skills',
        'syllabus',
        'strategies',
        'language',
        'program_id',
        'script_file_filename',
    ]

    @api.multi
    def accessCheck(self, user):
        for record in self:
            if user.partner_id.id == record.author_id.partner_id.id:
                return True
            else:
                return False
        return False

    @api.multi
    def readyForReview(self):
        for record in self:
            for k in self.required_review_fields:
                if not record[k]:
                    return False
        return True

    @api.multi
    def readyForRecording(self):
        for record in self:
            if record.sudo().author_id.videoCheck and record.state == 'script_approved' and record.panopto_id:
                return True
        return False

    @api.multi
    def missingFieldsForReview(self):
        for record in self:
            missing_fields = [
                f for f in self.required_review_fields if not record[f]]
            if missing_fields:
                return [record._fields[f].string for f in missing_fields]

    @api.multi
    def write(self, values):
        if 'state' in values:
            states = [k for k, v in self.states]
            if abs(states.index(self.state) - states.index(values['state'])) > 1:
                raise ValidationError(
                    _('You\'re not allowed to skip stages in this kanban!'))
            self.on_state_change(values['state'])
        super(GhuCourse, self).write(values)

    @api.one
    def approved(self, record):
        self.write({'state': 'script_approved'})

    @api.one
    def declined(self, record):
        self.write({'state': 'draft'})

    @api.model
    def _process_courses(self):
        """ Cron Job for creating Panopto folders for courses """
        _logger.info('Start Panopto Folder Generation')
        courses = self.env['ghu_custom_mba.course'].search(
            [('state', '=', 'script_approved')])
        for course in courses:
            if course.author_id.videoCheck and not course.panopto_id:
                course.createPanoptoFolder()

    def _stateLabel(self):
        return dict(self._fields['state'].selection).get(self.state)

    def on_state_change(self, new_state):
        # generate invoice
        if new_state == 'draft':
            if self.state == 'new':
                self.correctionNeeded()  # Send mail to advisor to review
        if new_state == 'new':
            self.reviewNeeded()  # Send mail to office and helmar to have a look
        elif new_state == 'script_approved':
            if self.state == 'new':
                # Create Panopto folder for course, add access rights for Lecturer and notify advisor
                self.scriptApproved()
                if self.author_id.videoCheck:
                    self.createPanoptoFolder()
        elif new_state == 'recording_finished':
            if self.state == 'script_approved':
                self.recordingReviewNeeded()
            print(new_state)  # Notify office to check video recording
        elif new_state == 'approved':
            print(new_state)  # Publish course on campus, notify Lecturer
        elif new_state == 'declined':
            print(new_state)  # Notify lecturer of reason why he was declined
        elif new_state == 'outdated':
            # Remove course from campus, notifiy lecturer to refactor
            print(new_state)

    def reviewNeeded(self):
        notification_template = self.env.ref(
            'ghu_custom_mba.review_needed_mail').sudo()
        notification_template.send_mail(
            self.id, raise_exception=False, force_send=False)
        return True

    def correctionNeeded(self):
        notification_template = self.env.ref(
            'ghu_custom_mba.correction_needed_mail').sudo()
        notification_template.send_mail(
            self.id, raise_exception=False, force_send=False)
        return True

    def scriptApproved(self):
        notification_template = self.env.ref(
            'ghu_custom_mba.script_approved_mail').sudo()
        notification_template.send_mail(
            self.id, raise_exception=False, force_send=False)
        return True

    def recordingReviewNeeded(self):
        notification_template = self.env.ref(
            'ghu_custom_mba.recording_review_needed_mail').sudo()
        notification_template.send_mail(
            self.id, raise_exception=False, force_send=False)
        return True

    @api.multi
    def createPanoptoFolder(self):
        for record in self:
            panopto = GhuPanopto(self.env)
            mainFolder = panopto.createFolder(record.name, record.id)
            scriptFolder = panopto.createFolder(
                "Lectures", str(record.id)+"-lectures", False, mainFolder)
            scriptFolder1 = panopto.createFolder("Lecture 1", str(
                record.id)+"-lectures1", False, scriptFolder)
            scriptFolder2 = panopto.createFolder("Lecture 2", str(
                record.id)+"-lectures2", False, scriptFolder)
            scriptFolder3 = panopto.createFolder("Lecture 3", str(
                record.id)+"-lectures3", False, scriptFolder)
            additionalFolder = panopto.createFolder(
                "Additional Information", str(record.id)+"-additional", False, mainFolder)
            self.write({'panopto_id': mainFolder})
            user = self.env['res.users'].search(
                [('partner_id', '=', record.author_id.partner_id.id)], limit=1)
            panoptoUserId = panopto.getUserId(user)
            panopto.grantAccessToFolder(mainFolder, panoptoUserId, 'Viewer')
            panopto.grantAccessToFolder(scriptFolder, panoptoUserId, 'Viewer')
            panopto.grantAccessToFolder(
                additionalFolder, panoptoUserId, 'Creator')
            panopto.grantAccessToFolder(
                scriptFolder1, panoptoUserId, 'Creator')
            panopto.grantAccessToFolder(
                scriptFolder2, panoptoUserId, 'Creator')
            panopto.grantAccessToFolder(
                scriptFolder3, panoptoUserId, 'Creator')
            _logger.info('Panopto Folder for ' + record.name + ' created')

    # Create corresponding product to buy in campus
    @api.model
    def create(self, vals):
        res = super(GhuCourse, self).create(vals)
        res.create_product()  # call your method
        return res

    @api.multi
    def create_product(self):
        for record in self:
            vals = {
                'name': record.name,
                'purchase_ok': False,
                'type': 'service',
                'lst_price': 990
            }
            if record.product_ref:
                product = record.product_ref
                product.name = record.name
                product.lst_price = 990
                product.write(vals)
            else:
                record.product_ref = self.env['product.product'].sudo().create(
                    vals)

    # Update product when name changes
    @api.onchange('name')  # if these fields are changed, call method
    def check_change(self):
        if self.product_ref and self.product_ref.name != self.name:
            product = self.product_ref
            product.write({'name': self.name})


class GhuAssessment(models.Model):
    _name = 'ghu_custom_mba.assessment'
    _rec_name = 'name'
    _description = "Assessment"

    course_id = fields.Many2one(
        string=u'Course',
        comodel_name='ghu_custom_mba.course',
        ondelete='cascade',
    )

    name = fields.Char('Name', size=128, required=True)

    types = [
        ('essay', 'Essay'),
        ('report', 'Report'),
        ('case_study', 'Case Study'),
        ('homework', 'Homework'),
        ('presentation', 'Presentation')
    ]

    type = fields.Selection(
        string=u'Assessment Type',
        selection=types
    )

    question_ids = fields.One2many(
        string=u'Questions',
        comodel_name='ghu_custom_mba.assessment_question',
        inverse_name='assessment_id',
    )


class GhuAssessmentQuestion(models.Model):
    _name = 'ghu_custom_mba.assessment_question'
    _rec_name = 'name'
    _description = "Assessment Question"

    name = fields.Char('Name', size=128, required=True)

    question = fields.Text('Question', required=True)

    assessment_id = fields.Many2one(
        string=u'assessment',
        comodel_name='ghu_custom_mba.assessment',
        ondelete='cascade',
    )
