# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import datetime
import logging
import json
import base64
import werkzeug
from ..util.blti import GhuBlti

_logger = logging.getLogger(__name__)


class GhuCustomMbaStudent(http.Controller):

    @http.route('/campus/courses/', auth='user', website=True)
    def list(self, **kw):
        return http.request.render('ghu_custom_mba.student_courselist', {
            'root': '/campus/course',
            'objects': http.request.env['ghu_custom_mba.course'].search([('state', '=', 'approved')]),
        })

    @http.route('/campus/course/preview/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def preview(self, obj, **kw):
        if obj.state == 'approved':
            return http.request.render('ghu_custom_mba.student_coursepreview', {
                'root': '/campus/course',
                'object': request.env['ghu_custom_mba.course'].sudo().browse(obj.id),
                'slug': 'campus_courses'
            })
        return http.request.not_found()

    @http.route('/campus/my/courses/', auth='user', website=True)
    def myCourses(self, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            enrollments = request.env['ghu_custom_mba.course_enrollment'].sudo().search([('student_ref', '=', 'ghu.student,'+str(student.id))])
            return http.request.render('ghu_custom_mba.student_mycourses', {
                'root': '/campus/course',
                'objects': enrollments,
            })
        return http.request.not_found()

    @http.route('/campus/course/buy/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def buyCourse(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        invoice_partners = request.env.user.partner_id.child_ids.filtered(
            lambda p: p.type == 'invoice')
        invoice = request.env['account.invoice'].sudo().create(dict(
            # customer (billing address)
            partner_id=invoice_partners[0].id if invoice_partners else request.env.user.partner_id.id,
            # customer (applicant)
            partner_shipping_id=request.env.user.partner_id.id,
            type='out_invoice',
            date_invoice=datetime.datetime.utcnow().date(),  # invoice date
            date_due=(datetime.datetime.utcnow() + \
                      datetime.timedelta(weeks=1)).date(),  # due date
            user_id=request.env().user.id,  # salesperson
            invoice_line_ids=[],  # invoice lines
            name=obj.product_ref.name,  # name for account move lines
            partner_bank_id=request.env['ir.config_parameter'].sudo().get_param(
                'ghu.automated_invoice_bank_account'),  # company bank account
        ))

        invoice_line = request.env['account.invoice.line'].sudo().with_context(
            type=invoice.type,
            journal_id=invoice.journal_id.id,
            default_invoice_id=invoice.id
        ).create(dict(
            product_id=obj.product_ref.id,
            name=obj.product_ref.name,
            price_unit=obj.product_ref.lst_price,
        ))

        invoice.invoice_line_ids = [(4, invoice_line.id)]
        invoice.action_invoice_open()
        invoice_template = request.env.ref('ghu.ghu_invoice_email_template').sudo()
        invoice_template.send_mail(invoice.id)
        invoice.write({'sent': True})

        student = request.env['ghu.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)

        enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().create(dict(
            invoice_ref='%s,%s' % ('account.invoice', invoice.id),
            course_ref='%s,%s' % ('ghu_custom_mba.course', obj.id),
            student_ref='%s,%s' % ('ghu.student', student.id),
            name=obj.name + '-' + student.name
        ))

        return http.request.redirect('/my/invoices/' + str(invoice.id))


    @http.route('/campus/course/take/<model("ghu_custom_mba.course"):obj>/', auth='user', website=True)
    def detail(self, obj, **kw):
        if request.env.user.partner_id.is_student:
            obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search([('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state != 'new':
                return http.request.render('ghu_custom_mba.student_takecourse', {
                    'root': '/campus/course',
                    'object': obj,
                    'enrollment': enrollment,
                    'slug': 'campus_my_course'
                })
        return http.request.not_found()