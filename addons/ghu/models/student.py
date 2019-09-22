# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class GhuStudentStudy(models.Model):
    _name = 'ghu.student.study'
    _description = 'Student Study Details'

    student_id = fields.Many2one('ghu.student', 'Student', ondelete="cascade")
    study_id = fields.Many2one('ghu.study', 'Course', required=True)

    _sql_constraints = [
        ('unique_name_student_study_number_id',
         'unique(study_id,student_id)',
         'Student can only study a study once!')
    ]


class GhuStudent(models.Model):
    _name = 'ghu.student'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Student"

    firstname = fields.Char(related='partner_id.firstname', required=True)
    lastname = fields.Char(related='partner_id.lastname', required=True)
    gender = fields.Selection(related='partner_id.gender', required=True)
    nationality = fields.Many2one('res.country', 'Nationality', required=True)
    date_of_birth = fields.Date(
        string=u'Date of Birth',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")

    academic_degree_pre = fields.Char(
        'Academic Degrees (Pre)',
        size=64,
    )
    academic_degree_post = fields.Char(
        'Academic Degrees (Post)',
        size=64,
    )
    native_language = fields.Many2one(
        string=u'Native Language',
        comodel_name='ghu.lang',
        required=True,
    )
    other_languages = fields.Many2many(
        string=u'Other Languages',
        comodel_name='ghu.lang',
        relation='ghu_student_lang_rel',
        column1='student_id',
        column2='lang_id'
    )
    email = fields.Char(related='partner_id.email', required=True)

    student_identification = fields.Char(
        string=u'Student Identification Number', compute='_compute_id', store=True)

    @api.depends('create_date')
    def _compute_id(self):
        for record in self:
            record.student_identification = "GHU-" + \
                record.create_date.strftime(
                    "%Y%m") + '{:05d}'.format(record.id + 1010)
