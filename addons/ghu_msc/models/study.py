# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class GhuStudy(models.Model):
    _inherit = 'ghu.study'
    mandatory_course_ids = fields.Many2many(
        comodel_name=u'ghu_custom_mba.course',
        string=u'Mandatory Courses',
        required=False
    )

    optional_course_ids = fields.Many2many(
        comodel_name='ghu_custom_mba.course',
        string=u'Optional Courses',
        required=False
    )

    optional_course_minimum = fields.Integer(string=u'Number of optional courses that have to be done')