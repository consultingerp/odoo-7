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
            'objects': http.request.env['ghu_custom_mba.course'].search([('state', '=','approved')]),
        })

    @http.route('/campus/course/preview/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def preview(self, obj, **kw):
        if obj.state == 'approved':
            return http.request.render('ghu_custom_mba.student_coursepreview', {
                'root': '/campus/course',
                'object': obj,
                'slug': 'campus_courses'
            })
        return http.request.not_found()


    @http.route('/campus/my/courses/', auth='user', website=True)
    def myCourses(self, **kw):
        if request.env.user.partner_id.is_student:
            partner_id = request.env.user.partner_id.id
            # TODO: Get all courses a partner/student bought
        return http.request.not_found()

    @http.route('campus/course/buy/<model("ghu_custom_mba.course"):obj>', auth='user', website=True)
    def buyCourse(self, obj, **kw):
        invoice_partners = request.env.user.partner_id.child_ids.filtered(lambda p: p.type == 'invoice')
        invoice = self.env['account.invoice'].create(dict(
            partner_id=invoice_partners[0].id if invoice_partners else request.env.user.partner_id.id, # customer (billing address)
            partner_shipping_id=request.env.user.partner_id.id, # customer (applicant)
            type='out_invoice',
            date_invoice=datetime.datetime.utcnow().date(), # invoice date
            date_due=(datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).date(), # due date
            user_id=self.env().user.id, # salesperson
            invoice_line_ids=[], # invoice lines
            name=obj.product_ref.name, # name for account move lines
            partner_bank_id=self.env['ir.config_parameter'].get_param('ghu.automated_invoice_bank_account'), # company bank account
        ))

        invoice_line = self.env['account.invoice.line'].with_context(
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
        invoice_template = self.env.ref('ghu.ghu_invoice_email_template')
        invoice_template.send_mail(invoice.id)
        invoice.write({'sent': True})

        return http.request.redirect('/my/invoices/'+invoice.id)

