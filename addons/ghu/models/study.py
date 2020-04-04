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

from odoo import models, fields


class GhuStudy(models.Model):
    _name = 'ghu.study'
    _description = "Study"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', size=16, required=True)

    section = fields.Char('Section', size=32, required=True)

    program_id = fields.Many2one(
        string=u'Program',
        comodel_name='ghu.program',
    )

    partner_university_id = fields.Many2one(
        string=u'Partner University',
        comodel_name='res.partner',
        required=False
    )

    product_id = fields.Many2one(
        string=u'Product',
        comodel_name='product.product',
        required=False
    )

    payment_term_id = fields.Many2many(
        string=u'Payment terms',
        comodel_name='account.payment.term'
    )

    description = fields.Html(string=u'Description')

    _sql_constraints = [
        ('unique_course_code',
         'unique(code)', 'Code should be unique per study!')]
