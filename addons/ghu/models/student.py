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

    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128)
    birth_date = fields.Date('Birth Date')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'),
         ('o', 'Other')], 'Gender')
    nationality = fields.Many2one('res.country', 'Nationality')

    already_partner = fields.Boolean('Already Partner')
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")

    _sql_constraints = [
        ('unique_gr_no',
         'unique(gr_no)',
         'Gr Number Must be unique!')
    ]

    @api.multi
    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))