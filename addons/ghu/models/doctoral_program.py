# -*- coding: utf-8 -*-

import datetime
import logging
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class GhuDoctoralProgram(models.Model):
    _name = 'ghu.doctoral_program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GHU Doctoral Program'

    study_ref = fields.Reference(
        string='Study',
        selection=[('ghu.study', 'Stucy')]
    )

    thesis_title = fields.Char(
        string='Thesis Title',
    )
    
    advisor_ref = fields.Reference(
        string=u'Advisor',
        selection=[('ghu.advisor', 'Advisor')]
    )

    student_ref = fields.Reference(
        string=u'Student',
        selection=[('ghu.student', 'Student')]
    )

    # Modules
    # Phase 1

    phase1_modules = [
        ['proposal',
         'writing',
         'reflection'],
        'expose']

    phase2_modules = [
        'thesis',
        'paper',
        'defensio'
    ]

    proposal_id = fields.Many2one(
        string='Proposal',
        comodel_name='ghu.doctoral_program_proposal',
        ondelete='restrict',
    )

    professional_capability_id = fields.Many2one(
        string='Professional Capability',
        comodel_name='ghu.doctoral_program_professional_capability',
        ondelete='restrict',
    )

    expose_id = fields.Many2one(
        string='Professional Capability',
        comodel_name='ghu.doctoral_program_expose',
        ondelete='restrict',
    )

    expose_id = fields.Many2one(
        string='Expose',
        comodel_name='ghu.doctoral_program_expose',
        ondelete='restrict',
    )

    dissertation_id = fields.Many2one(
        string='Dissertation',
        comodel_name='ghu.doctoral_program_dissertation',
        ondelete='restrict',
    )

    paper_id = fields.Many2one(
        string='Paper',
        comodel_name='ghu.doctoral_program_paper',
        ondelete='restrict',
    )

    defensio_id = fields.Many2one(
        string='Defensio',
        comodel_name='ghu.doctoral_program_defensio',
        ondelete='restrict',
    )




class GhuModule(models.Model):
    _name = 'ghu.doctoral_program_module'
    _description = 'GHU Basic Module'

    attachment = fields.Binary(string='Attachment', attachment=True)

    passed = fields.Boolean(
        string='Passed',
    )

    assessment_report_native = fields.Text(
        string='Feedback native language',
    )

    assessment_report_english = fields.Text(
        string='Feedback english',
    )
class GhuProposal(models.Model):
    _name = 'ghu.doctoral_program_proposal'
    _description = 'GHU Doctoral Program'

    _inherit = ['ghu.doctoral_program_module']

    title_feedback = fields.Text(
        string='Title Feedback',
    )

    abstract_feedback = fields.Text(
        string='Abstract Feedback',
    )

    context_feedback = fields.Text(
        string='Context Feedback',
    )

    question_feedback = fields.Text(
        string='Question Feedback',
    )

    method_feedback = fields.Text(
        string='Method Feedback',
    )

    significance_feedback = fields.Text(
        string='Significance Feedback',
    )

    writing_style = fields.Text(
        string='Writing Style',
    )

    spelling_grammar = fields.Text(
        string='Spelling Grammar',
    )
class GhuAcademicWriting(models.Model):
    _name = 'ghu.doctoral_program_academic_writing'
    _description = 'GHU Doctoral Program - Academic Writing'

    _inherit = ['ghu.doctoral_program_module']
    
class GhuProfessionalCapability(models.Model):
    _name = 'ghu.doctoral_program_professional_capability'
    _description = 'GHU Doctoral Program - Professional Capability'

    _inherit = ['ghu.doctoral_program_module']

    presentation = fields.Text(
        string='Presentation',
    )

    presentation_score = fields.Float(
        string='Presentation Score',
    )

    @api.one
    @api.constrains('presentation_score')
    def _check_presentation(self):
        if self.presentation_score > 15.0 or self.presentation_score < 0.0:
            raise ValidationError(
                "Presentation score must be between 0 and 15 points.")

    career = fields.Text(
        string='Career',
    )

    career_score = fields.Float(
        string='Career Score',
    )

    @api.one
    @api.constrains('career_score')
    def _check_career(self):
        if self.career_score > 20.0 or self.career_score < 0.0:
            raise ValidationError(
                "Career score must be between 0 and 20 points.")

    competences = fields.Text(
        string='Competences',
    )

    competences_score = fields.Float(
        string='Competence Score',
    )

    @api.one
    @api.constrains('competences_score')
    def _check_competences(self):
        if self.competences_score > 20.0 or self.competences_score < 0.0:
            raise ValidationError(
                "Competence score must be between 0 and 20 points.")

    ethics = fields.Text(
        string='Ethics',
    )

    ethics_score = fields.Float(
        string='Ethics Score',
    )

    @api.one
    @api.constrains('ethics_score')
    def _check_ethics(self):
        if self.ethics_score > 15.0 or self.ethics_score < 0.0:
            raise ValidationError(
                "Ethics score must be between 0 and 15 points.")

    foresight = fields.Text(
        string='Foresight',
    )

    foresight_score = fields.Float(
        string='Foresight Score',
    )

    @api.one
    @api.constrains('foresight_score')
    def _check_foresight(self):
        if self.foresight_score > 20.0 or self.foresight_score < 0.0:
            raise ValidationError(
                "Foresight score must be between 0 and 20 points.")

    writing = fields.Text(
        string='Writing',
    )

    writing_score = fields.Float(
        string='Writing Score',
    )

    @api.one
    @api.constrains('writing_score')
    def _check_writing(self):
        if self.writing_score > 10.0 or self.writing_score < 0.0:
            raise ValidationError(
                "Writing score must be between 0 and 10 points.")

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score'
    )

    @api.depends('writing_score', 'foresight_score', 'ethics_score', 'competences_score', 'career_score', 'presentation_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = record.writing_score + record.foresight_score + record.ethics_score + \
                record.competences_score + record.career_score + record.presentation_score

    @api.onchange('total_score')  # if these fields are changed, call method
    def check_change(self):
        if self.total_score >= 50.0:
            self.passed = True
        else:
            self.passed = False
class GhuExpose(models.Model):
    _name = 'ghu.doctoral_program_expose'
    _description = 'GHU Doctoral Program - Expose'

    _inherit = ['ghu.doctoral_program_module']

    formatting = fields.Text(
        string='Formatting',
    )

    formatting_score = fields.Float(
        string='Formatting Score',
    )

    @api.one
    @api.constrains('formatting_score')
    def _check_formatting(self):
        if self.formatting_score > 20.0 or self.formatting_score < 0.0:
            raise ValidationError(
                "Formatting score must be between 0 and 20 points.")

    readability = fields.Text(
        string='Readability',
    )

    readability_score = fields.Float(
        string='Readability Score',
    )

    @api.one
    @api.constrains('readability_score')
    def _check_readability(self):
        if self.readability_score > 20.0 or self.readability_score < 0.0:
            raise ValidationError(
                "Readability score must be between 0 and 20 points.")

    organization = fields.Text(
        string='Organization',
    )

    organization_score = fields.Float(
        string='Organization Score',
    )

    @api.one
    @api.constrains('organization_score')
    def _check_organization(self):
        if self.organization_score > 20.0 or self.organization_score < 0.0:
            raise ValidationError(
                "Organization score must be between 0 and 20 points.")

    components = fields.Text(
        string='Components',
    )

    components_score = fields.Float(
        string='Components Score',
    )

    @api.one
    @api.constrains('components_score')
    def _check_components(self):
        if self.components_score > 20.0 or self.components_score < 0.0:
            raise ValidationError(
                "Components score must be between 0 and 20 points.")

    guidelines = fields.Text(
        string='Guidelines',
    )

    guidelines_score = fields.Float(
        string='Guidelines Score',
    )

    @api.one
    @api.constrains('guidelines_score')
    def _check_guidelines(self):
        if self.guidelines_score > 20.0 or self.guidelines_score < 0.0:
            raise ValidationError(
                "Guidelines score must be between 0 and 20 points.")

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score'
    )

    @api.depends('guidelines_score', 'components_score', 'organization_score', 'readability_score', 'formatting_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = record.guidelines_score + record.components_score + \
                record.organization_score + record.readability_score + record.formatting_score

    @api.onchange('total_score')  # if these fields are changed, call method
    def check_change(self):
        if self.total_score >= 50.0:
            self.passed = True
        else:
            self.passed = False
class GhuDissertation(models.Model):
    _name = 'ghu.doctoral_program_dissertation'
    _description = 'GHU Doctoral Program - Dissertation'

    _inherit = ['ghu.doctoral_program_module']

    title = fields.Text(
        string='Title',
    )

    title_score = fields.Float(
        string='Title Score',
    )

    @api.one
    @api.constrains('title_score')
    def _check_title(self):
        if self.title_score > 20.0 or self.title_score < 0.0:
            raise ValidationError(
                "Title score must be between 0 and 20 points.")

    research = fields.Text(
        string='Research',
    )

    research_score = fields.Float(
        string='Research Score',
    )

    @api.one
    @api.constrains('research_score')
    def _check_research(self):
        if self.research_score > 20.0 or self.research_score < 0.0:
            raise ValidationError(
                "Research score must be between 0 and 20 points.")

    organization = fields.Text(
        string='Organization',
    )

    organization_score = fields.Float(
        string='Organization Score',
    )

    @api.one
    @api.constrains('organization_score')
    def _check_organization(self):
        if self.organization_score > 20.0 or self.organization_score < 0.0:
            raise ValidationError(
                "Organization score must be between 0 and 20 points.")

    method = fields.Text(
        string='Method',
    )

    method_score = fields.Float(
        string='Method Score',
    )

    @api.one
    @api.constrains('method_score')
    def _check_method(self):
        if self.method_score > 20.0 or self.method_score < 0.0:
            raise ValidationError(
                "Method score must be between 0 and 20 points.")

    guidelines = fields.Text(
        string='Guidelines',
    )

    guidelines_score = fields.Float(
        string='Guidelines Score',
    )

    @api.one
    @api.constrains('guidelines_score')
    def _check_guidelines(self):
        if self.guidelines_score > 20.0 or self.guidelines_score < 0.0:
            raise ValidationError(
                "Guidelines score must be between 0 and 20 points.")

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score'
    )

    @api.depends('guidelines_score', 'method_score', 'organization_score', 'research_score', 'title_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = record.guidelines_score + record.method_score + record.organization_score + \
                record.research_score + record.title_score

    @api.onchange('total_score')  # if these fields are changed, call method
    def check_change(self):
        if self.total_score >= 50.0:
            self.passed = True
        else:
            self.passed = False
class GhuPaper(models.Model):
    _name = 'ghu.doctoral_program_paper'
    _description = 'GHU Doctoral Program - Research Paper'

    _inherit = ['ghu.doctoral_program_module']

    formatting = fields.Text(
        string='Formatting',
    )

    formatting_score = fields.Float(
        string='Formatting Score',
    )

    @api.one
    @api.constrains('formatting_score')
    def _check_formatting(self):
        if self.formatting_score > 20.0 or self.formatting_score < 0.0:
            raise ValidationError(
                "Formatting score must be between 0 and 20 points.")

    readability = fields.Text(
        string='Readability',
    )

    readability_score = fields.Float(
        string='Readability Score',
    )

    @api.one
    @api.constrains('readability_score')
    def _check_readability(self):
        if self.readability_score > 20.0 or self.readability_score < 0.0:
            raise ValidationError(
                "Readability score must be between 0 and 20 points.")

    organization = fields.Text(
        string='Organization',
    )

    organization_score = fields.Float(
        string='Organization Score',
    )

    @api.one
    @api.constrains('organization_score')
    def _check_organization(self):
        if self.organization_score > 20.0 or self.organization_score < 0.0:
            raise ValidationError(
                "Organization score must be between 0 and 20 points.")

    components = fields.Text(
        string='Components',
    )

    components_score = fields.Float(
        string='Components Score',
    )

    @api.one
    @api.constrains('components_score')
    def _check_components(self):
        if self.components_score > 20.0 or self.components_score < 0.0:
            raise ValidationError(
                "Components score must be between 0 and 20 points.")

    guidelines = fields.Text(
        string='Guidelines',
    )

    guidelines_score = fields.Float(
        string='Guidelines Score',
    )

    @api.one
    @api.constrains('guidelines_score')
    def _check_guidelines(self):
        if self.guidelines_score > 20.0 or self.guidelines_score < 0.0:
            raise ValidationError(
                "Guidelines score must be between 0 and 20 points.")

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score'
    )

    @api.depends('guidelines_score', 'components_score', 'organization_score', 'readability_score', 'formatting_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = record.guidelines_score + record.components_score + \
                record.organization_score + record.readability_score + record.formatting_score

    @api.onchange('total_score')  # if these fields are changed, call method
    def check_change(self):
        if self.total_score >= 50.0:
            self.passed = True
        else:
            self.passed = False
class GhuDefensio(models.Model):
    _name = 'ghu.doctoral_program_defensio'
    _description = 'GHU Doctoral Program - Defensio'

    _inherit = ['ghu.doctoral_program_module']

    research = fields.Text(
        string='Research',
    )

    research_score = fields.Float(
        string='Research Score',
    )

    @api.one
    @api.constrains('research_score')
    def _check_research(self):
        if self.research_score > 20.0 or self.research_score < 0.0:
            raise ValidationError(
                "Research score must be between 0 and 20 points.")

    organization = fields.Text(
        string='Organization',
    )

    organization_score = fields.Float(
        string='Organization Score',
    )

    @api.one
    @api.constrains('organization_score')
    def _check_organization(self):
        if self.organization_score > 20.0 or self.organization_score < 0.0:
            raise ValidationError(
                "Organization score must be between 0 and 20 points.")

    method = fields.Text(
        string='Method',
    )

    method_score = fields.Float(
        string='Method Score',
    )

    @api.one
    @api.constrains('method_score')
    def _check_method(self):
        if self.method_score > 20.0 or self.method_score < 0.0:
            raise ValidationError(
                "Method score must be between 0 and 20 points.")

    traceability = fields.Text(
        string='Traceability',
    )

    traceability_score = fields.Float(
        string='Traceability Score',
    )

    @api.one
    @api.constrains('traceability_score')
    def _check_traceability(self):
        if self.traceability_score > 20.0 or self.traceability_score < 0.0:
            raise ValidationError(
                "Traceability score must be between 0 and 20 points.")

    guidelines = fields.Text(
        string='Guidelines',
    )

    guidelines_score = fields.Float(
        string='Guidelines Score',
    )

    @api.one
    @api.constrains('guidelines_score')
    def _check_guidelines(self):
        if self.guidelines_score > 20.0 or self.guidelines_score < 0.0:
            raise ValidationError(
                "Guidelines score must be between 0 and 20 points.")

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score'
    )

    @api.depends('guidelines_score', 'method_score', 'organization_score', 'research_score', 'traceability_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = record.guidelines_score + record.method_score + record.organization_score + \
                record.research_score + record.traceability_score

    @api.onchange('total_score')  # if these fields are changed, call method
    def check_change(self):
        if self.total_score >= 50.0:
            self.passed = True
        else:
            self.passed = False

    
