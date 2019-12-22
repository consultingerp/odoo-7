# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)


class GhuPartner(models.Model):
    _inherit = 'res.partner'

    is_advisor = fields.Boolean(
        string=u'Is advisor?',
        compute='_is_advisor',
        search='_search_advisor'
    )

    is_student = fields.Boolean(
        string=u'Is student?',
        compute='_is_student',
        search='_search_student'
    )

    is_custom_mba = fields.Boolean(
        string=u'Is custom MBA?',
        compute='_is_custom_mba',
        search='_search_custom_mba'
    )

    is_custom_mba_student = fields.Boolean(
        string=u'Is custom MBA student?',
        compute='_is_cba_student',
        search='_search_cba_student'
    )


    is_doctoral_student = fields.Boolean(
        string=u'Is doctoral student?',
        compute='_is_doctoral_student',
        search='_search_doctoral_student'
    )

    def _is_advisor(self):
        for record in self:
            if self.env['ghu.advisor'].sudo().search([('partner_id', '=', record.id)]):
                record.is_advisor = True
            else:
                record.is_advisor = False
    
    def _search_advisor(self, operator, value):
        recs = self.env['ghu.advisor'].sudo().search([]).filtered(lambda x : x.partner_id )
        if recs:
            return [('id', 'in', [x.partner_id.id for x in recs])]

    def _is_student(self):
        for record in self:
            if self.env['ghu.student'].sudo().search([('partner_id', '=', record.id)]):
                record.is_student = True
            else:
                record.is_student = False
                
    def _search_student(self, operator, value):
        recs = self.env['ghu.student'].sudo().search([]).filtered(lambda x : x.partner_id )
        if recs:
            return [('id', 'in', [x.partner_id.id for x in recs])]

    
    def _is_cba_student(self):
        for record in self:
            if self.env['ghu.student'].sudo().search([('partner_id', '=', record.id),('custom_mba','=',True)]):
                record.is_custom_mba_student = True
            else:
                record.is_custom_mba_student = False
                
    def _search_cba_student(self, operator, value):
        recs = self.env['ghu.student'].sudo().search([('custom_mba','=',True)]).filtered(lambda x : x.partner_id )
        if recs:
            return [('id', 'in', [x.partner_id.id for x in recs])]

        
    def _is_doctoral_student(self):
        for record in self:
            if self.env['ghu.student'].sudo().search([('partner_id', '=', record.id),('doctoral_student','=',True)]):
                record.is_doctoral_student = True
            else:
                record.is_doctoral_student = False
                
    def _search_doctoral_student(self, operator, value):
        recs = self.env['ghu.student'].sudo().search([('doctoral_student','=',True)]).filtered(lambda x : x.partner_id )
        if recs:
            return [('id', 'in', [x.partner_id.id for x in recs])]

    def _is_custom_mba(self):
        for record in self:
            if record.is_advisor:
                advisor = self.env['ghu.advisor'].sudo().search(
                    [('partner_id', '=', record.id)], limit=1)
                if advisor.is_cafeteria:
                    record.is_custom_mba = True
                else:
                    record.is_custom_mba = False

    def _search_custom_mba(self, operator, value):
        recs = self.env['ghu.advisor'].sudo().search([]).filtered(lambda x : x.is_cafeteria is True )
        if recs:
            return [('id', 'in', [x.partner_id.id for x in recs])]