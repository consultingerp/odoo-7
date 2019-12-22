# -*- coding: utf-8 -*-
from odoo import http
from odoo import api, fields, models, tools
from odoo.http import request
import datetime
from datetime import date
import logging
import json
import base64
import werkzeug
import random
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
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            return http.request.render('ghu_custom_mba.student_coursepreview', {
                'root': '/campus/course',
                'student': student,
                'object': request.env['ghu_custom_mba.course'].sudo().browse(obj.id),
                'slug': 'campus_courses'
            })
        return http.request.not_found()

    @http.route('/campus/my/courses/', auth='user', website=True)
    def myCourses(self, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollments = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id))])
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
        invoice_template = request.env.ref(
            'ghu_custom_mba.course_invoice_email_template').sudo()
        invoice_template.send_mail(invoice.id)
        invoice.write({'sent': True})

        student = request.env['ghu.student'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)], limit=1)

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
            blti = GhuBlti()
            params = blti.createParams(request.env['ir.config_parameter'].sudo().get_param(
                'ghu.panopto_blti_consumer_key'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_consumer_secret'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_launch_url'), 'private-'+str(request.env.user.id), request.env.user.id, request.env.user.name, request.env.user.firstname, request.env.user.lastname, request.env.user.email)
            obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state != 'new':
                return http.request.render('ghu_custom_mba.student_takecourse', {
                    'bltiParams': params,
                    'root': '/campus/course',
                    'object': obj,
                    'enrollment': enrollment,
                    'slug': 'campus_my_course'
                })
        return http.request.not_found()

    @http.route('/campus/course/request_assessment/<model("ghu_custom_mba.course"):obj>/', auth='user', website=True)
    def requestAssessment(self, obj, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state != 'new':
                return http.request.render('ghu_custom_mba.student_requestassessment', {
                    'root': '/campus/course',
                    'object': obj,
                    'enrollment': enrollment,
                    'slug': 'campus_my_course'
                })
        return http.request.not_found()

    @http.route('/campus/course/create_assessment/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def createAssessment(self, obj, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state != 'new':
                assessment = enrollment.course_ref.assessment_ids[0]
                question = random.choice(assessment.question_ids)
                ex = request.env['ghu_custom_mba.examination'].sudo().create({
                    'type': assessment.type,
                    'question_title': question.name,
                    'question': question.question,
                    'request_date': datetime.datetime.utcnow().date(),
                    'enrollment_id': enrollment.id
                })
                enrollment.sudo().write({
                    'examination_count': enrollment.examination_count + 1,
                    'state': 'examination'
                })
                return werkzeug.utils.redirect('/campus/course/'+str(obj.id)+'/assessment/'+str(ex.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.examination"):ex>', auth='user', website=True)
    def showAssessment(self, obj, ex, **kw):
        ex = request.env['ghu_custom_mba.examination'].sudo().browse(ex.id)
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state == 'examination':
                return http.request.render('ghu_custom_mba.student_showexamination', {
                    'root': '/campus/course',
                    'object': obj.sudo(),
                    'enrollment': enrollment,
                    'ex': ex,
                    'slug': 'campus_my_course'
                })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/examination/submit/<model("ghu_custom_mba.examination"):ex>', type='http', auth="user", methods=['POST'], website=True)
    def saveSubmission(self, obj, ex, **post):
        ex = request.env['ghu_custom_mba.examination'].sudo().browse(ex.id)
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            student = request.env['ghu.student'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            enrollment = request.env['ghu_custom_mba.course_enrollment'].sudo().search(
                [('student_ref', '=', 'ghu.student,'+str(student.id)), ('course_ref', '=', 'ghu_custom_mba.course,'+str(obj.id))], limit=1)
            if enrollment and enrollment.state == 'examination':
                if post.get('attachment',False):
                    attachments = request.env['ir.attachment']
                    name = post.get('attachment').filename      
                    file = post.get('attachment')
                    attachment = file.read() 
                    ex.sudo().write({
                        'submission': base64.b64encode(attachment),
                        'submission_filename': name
                    })
                    enrollment.sudo().write({'state':'grading'})
                    return request.render('ghu_custom_mba.student_examination_submitted',{
                        'object': obj.sudo()
                    })
        return werkzeug.utils.redirect('/campus/course/'+str(obj.id)+'/assessment/'+str(ex.id))