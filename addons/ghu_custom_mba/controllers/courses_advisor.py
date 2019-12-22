# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json
import base64
import werkzeug
from ..util.blti import GhuBlti

_logger = logging.getLogger(__name__)


class GhuCustomMba(http.Controller):
    @http.route('/campus/manage/courses/', auth='user', website=True)
    def listMyCourses(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            partner_id = request.env.user.partner_id.id
            advisor = request.env['ghu.advisor'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            advisor_id = advisor.id
            if advisor_id:
                objects = request.env['ghu_custom_mba.course'].search(
                    [('author_id', '=', advisor_id)])
                _logger.info('fetch of courses succeeded')
                return http.request.render('ghu_custom_mba.courselist', {
                    'root': '/campus/course',
                    'author': 'true',
                    'objects': objects,
                    'slug': 'campus_manage_courses'
                })
        return http.request.not_found()

    @http.route('/campus/grading/courses/', auth='user', website=True)
    def gradeMyCourses(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            partner_id = request.env.user.partner_id.id
            advisor = request.env['ghu.advisor'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            advisor_id = advisor.id
            if advisor_id:
                examinations = request.env['ghu_custom_mba.course_enrollment'].sudo().search([('state','=','grading')])
                objects = [(i) for i in examinations if i.course_ref.author_id.id==advisor_id]
                _logger.info('fetch of courses to grade succeeded')
                return http.request.render('ghu_custom_mba.coursegradinglist', {
                    'objects': objects,
                    'slug': 'campus_grading_courses'
                })
        return http.request.not_found()

    @http.route('/campus/course/grade/<model("ghu_custom_mba.course_enrollment"):obj>', auth='user', website=True)
    def gradeCourse(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course_enrollment'].sudo().browse(
            obj.id)
        if obj.course_ref.author_id.partner_id.id == request.env.user.partner_id.id:
            examination = request.env['ghu_custom_mba.examination'].sudo().search(
                [('enrollment_id', '=', obj.id), ('submission_filename', '!=', '')])
            return http.request.render('ghu_custom_mba.coursegradingdetail', {
                'enrollment': obj,
                'examination': examination,
                'slug': 'campus_grading_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/grade/save/<model("ghu_custom_mba.examination"):obj>', auth='user', website=True)
    def saveGradeCourse(self, obj, **kw):
        obj = request.env['ghu_custom_mba.examination'].sudo().browse(obj.id)
        if obj.enrollment_id.course_ref.author_id.partner_id.id == request.env.user.partner_id.id:
            obj.write(kw)
            if obj.grade >= 25:
                obj.course_ref.write({'state':'completed'})
            else:
                obj.course_ref.write({'state':'failed'})
            return werkzeug.utils.redirect('/campus/grading/courses/')
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/', auth='user', website=True)
    def detail(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if obj.accessCheck(request.env.user):
            return http.request.render('ghu_custom_mba.coursedetail', {
                'root': '/campus/course',
                'object': obj,
                'author': 'true',
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/my/video', methods=['GET'], auth='user', website=True)
    def video(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            blti = GhuBlti()
            params = blti.createParams(request.env['ir.config_parameter'].sudo().get_param(
                'ghu.panopto_blti_consumer_key'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_consumer_secret'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_launch_url'), 'private-'+str(request.env.user.id), request.env.user.id, request.env.user.name, request.env.user.firstname, request.env.user.lastname, request.env.user.email)
            partner_id = request.env.user.partner_id.id
            advisor = request.env['ghu.advisor'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1)
            return http.request.render('ghu_custom_mba.myvideos', {
                'bltiParams': params,
                'advisor': advisor,
                'slug': 'campus_my_video'
            })
        return http.request.not_found()

    @http.route('/campus/course/new', methods=['GET'], auth='user', website=True)
    def new(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            course_model = request.env['ir.model'].sudo().search(
                [('model', '=', 'ghu_custom_mba.course')])
            course_fields = request.env['ir.model.fields'].sudo().search([
                ('model_id', '=', course_model.id),
            ])
            all_fields = dict()
            for f in course_fields:
                all_fields[f['name']] = ''
            languages = request.env['ghu.lang'].sudo().search(
                [('name', '!=', '')])
            programs = request.env['ghu.program'].sudo().search([])
            return http.request.render('ghu_custom_mba.courseedit', {
                'root': '/campus/course',
                'new': True,
                'object': all_fields,
                'languages': languages,
                'programs': programs,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/edit', methods=['GET'], auth='user', website=True)
    def edit(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            languages = request.env['ghu.lang'].sudo().search(
                [('name', '!=', '')])
            programs = request.env['ghu.program'].sudo().search([])
            return http.request.render('ghu_custom_mba.courseedit', {
                'root': '/campus/course',
                'object': obj,
                'author': 'true',
                'languages': languages,
                'programs': programs,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/record', methods=['GET'], auth='user', website=True)
    def record(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            blti = GhuBlti()
            params = blti.createParams(request.env['ir.config_parameter'].sudo().get_param(
                'ghu.panopto_blti_consumer_key'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_consumer_secret'),
                request.env['ir.config_parameter'].sudo().get_param(
                    'ghu.panopto_blti_launch_url'), 'private-'+str(request.env.user.id), request.env.user.id, request.env.user.name, request.env.user.firstname, request.env.user.lastname, request.env.user.email)
            return http.request.render('ghu_custom_mba.courserecord', {
                'root': '/campus/course',
                'object': obj,
                'author': 'true',
                'bltiParams': params,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/panopto', methods=['GET'], auth='user', website=True)
    def panopto(self, **kw):
        blti = GhuBlti()
        params = blti.createParams(request.env['ir.config_parameter'].sudo().get_param(
            'ghu.panopto_blti_consumer_key'),
            request.env['ir.config_parameter'].sudo().get_param(
                'ghu.panopto_blti_consumer_secret'),
            request.env['ir.config_parameter'].sudo().get_param(
                'ghu.panopto_blti_launch_url'), 'private-'+str(request.env.user.id), request.env.user.id, request.env.user.name, request.env.user.firstname, request.env.user.lastname, request.env.user.email)
        return http.request.render('ghu_custom_mba.panopto', {
            'root': '/campus',
            'bltiParams': params,
            'slug': 'campus_panopto'
        })

    @http.route('/campus/course/save/', methods=['POST'], auth='user', website=True)
    def create(self, **kw):
        if request.env.user.partner_id.is_custom_mba:
            partner_id = request.env.user.partner_id.id
            advisor_id = request.env['ghu.advisor'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1).id
            kw['author_id'] = advisor_id
            kw['status'] = 'draft'
            for key in list(kw.keys()):
                if hasattr(kw[key], 'filename'):
                    value = kw.pop(key)
                    kw[(key + '_filename')] = value.filename
                    kw[key] = base64.b64encode(value.read())
            course_record = request.env['ghu_custom_mba.course'].with_context(
                mail_create_nosubscribe=True).create(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(course_record.id))
        return http.request.not_found()

    @http.route('/campus/course/save/<model("ghu_custom_mba.course"):obj>', methods=['POST'], auth='user', website=True)
    def update(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            for key in list(kw.keys()):
                if hasattr(kw[key], 'filename'):
                    value = kw.pop(key)
                    kw[(key + '_filename')] = value.filename
                    kw[key] = base64.b64encode(value.read())
            kw['status'] = 'draft'
            for key in list(kw.keys()):
                if not kw[key]:
                    del kw[key]
            obj.write(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/review', methods=['GET'], auth='user', website=True)
    def review(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            if obj.readyForReview() and obj.readyForRecording():
                kw = dict()
                kw['state'] = 'recording_finished'
                obj.write(kw)
            elif obj.readyForReview():
                kw = dict()
                kw['state'] = 'new'
                obj.write(kw)
            return werkzeug.utils.redirect('/campus/manage/courses')
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/new', methods=['GET'], auth='user', website=True)
    def newAssessment(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            assessment_model = request.env['ir.model'].sudo().search(
                [('model', '=', 'ghu_custom_mba.assessment')])
            assessment_fields = request.env['ir.model.fields'].sudo().search([
                ('model_id', '=', assessment_model.id),
            ])
            all_fields = dict()
            for f in assessment_fields:
                all_fields[f['name']] = ''

            return http.request.render('ghu_custom_mba.assessment_edit', {
                'root': '/campus/course',
                'new': True,
                'course': obj,
                'types': request.env['ghu_custom_mba.assessment'].types,
                'object': all_fields,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/edit/<model("ghu_custom_mba.assessment"):ass>', methods=['GET'], auth='user', website=True)
    def editAssessment(self, obj, ass, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            return http.request.render('ghu_custom_mba.assessment_edit', {
                'root': '/campus/course',
                'new': True,
                'course': obj,
                'types': request.env['ghu_custom_mba.assessment'].types,
                'object': ass,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/delete/<model("ghu_custom_mba.assessment"):ass>', methods=['GET'], auth='user', website=True)
    def deleteAssessment(self, obj, ass, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            ass.unlink()
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/save/', methods=['POST'], auth='user', website=True)
    def createAssessment(self, obj, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            kw['course_id'] = obj.id
            for key in list(kw.keys()):
                if hasattr(kw[key], 'filename'):
                    value = kw.pop(key)
                    kw[(key + '_filename')] = value.filename
                    kw[key] = base64.b64encode(value.read())
            assessment_record = request.env['ghu_custom_mba.assessment'].with_context(
                mail_create_nosubscribe=True).create(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/save/<model("ghu_custom_mba.assessment"):ass>', methods=['POST'], auth='user', website=True)
    def updateAssessment(self, obj, ass, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            for key in list(kw.keys()):
                if hasattr(kw[key], 'filename'):
                    value = kw.pop(key)
                    kw[(key + '_filename')] = value.filename
                    kw[key] = base64.b64encode(value.read())
            for key in list(kw.keys()):
                if not kw[key]:
                    del kw[key]
            ass.write(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.assessment"):ass>/question/new', methods=['GET'], auth='user', website=True)
    def newAssessmentQuestion(self, obj, ass, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            question_model = request.env['ir.model'].sudo().search(
                [('model', '=', 'ghu_custom_mba.assessment_question')])
            question_fields = request.env['ir.model.fields'].sudo().search([
                ('model_id', '=', question_model.id),
            ])
            all_fields = dict()
            for f in question_fields:
                all_fields[f['name']] = ''

            return http.request.render('ghu_custom_mba.question_edit', {
                'root': '/campus/course',
                'new': True,
                'course': obj,
                'ass': ass,
                'object': all_fields,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.assessment"):ass>/question/edit/<model("ghu_custom_mba.assessment_question"):question>', methods=['GET'], auth='user', website=True)
    def editAssessmentQuestion(self, obj, ass, question, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            return http.request.render('ghu_custom_mba.question_edit', {
                'root': '/campus/course',
                'new': True,
                'course': obj,
                'ass': ass,
                'object': question,
                'slug': 'campus_manage_courses'
            })
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.assessment"):ass>/question/save/', methods=['POST'], auth='user', website=True)
    def createAssessmentQuestion(self, obj, ass, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            kw['assessment_id'] = ass.id
            question_record = request.env['ghu_custom_mba.assessment_question'].with_context(
                mail_create_nosubscribe=True).create(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id)+'/assessment/edit/'+str(ass.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.assessment"):ass>/question/save/<model("ghu_custom_mba.assessment_question"):question>', methods=['POST'], auth='user', website=True)
    def updateAssessmentQuestion(self, obj, ass, question, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            kw['assessment_id'] = ass.id
            question.write(kw)
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id)+'/assessment/edit/'+str(ass.id))
        return http.request.not_found()

    @http.route('/campus/course/<model("ghu_custom_mba.course"):obj>/assessment/<model("ghu_custom_mba.assessment"):ass>/question/delete/<model("ghu_custom_mba.assessment_question"):question>', methods=['GET'], auth='user', website=True)
    def deleteAssessmentQuestion(self, obj, ass, question, **kw):
        obj = request.env['ghu_custom_mba.course'].sudo().browse(obj.id)
        if request.env.user.partner_id.id == obj.author_id.partner_id.id:
            question.unlink()
            return werkzeug.utils.redirect('/campus/course/'+str(obj.id)+'/assessment/edit/'+str(ass.id))
        return http.request.not_found()
