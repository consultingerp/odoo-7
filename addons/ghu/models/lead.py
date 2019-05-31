from odoo import fields, models, api
import re

class Lead(models.Model):
    _inherit = 'crm.lead'
    study_id = fields.Many2one(
        'ghu.study', 'Study', required=False)
        
    nationality = fields.Many2one(
        string=u'Nationality',
        comodel_name='res.country',
        required=False)

    highest_degree = fields.Char(
        string=u'Highest Degree',
    )

    # Convert created lead from external partners to correct lead
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        if re.search(r'\S+@zapiermail.com', msg_dict.get('from')).group(0):
            defaults = {
                'name':  re.search(r'First and Last Name: ([\S .]+)', msg_dict.get('body')).group(0),
                'email_from': re.search(r'Email address: ([\S .]+)', msg_dict.get('body')).group(0),
                'phone': re.search(r'Phone Number or Skype: ([\S .]+)', msg_dict.get('body')).group(0),
                'highest_degree': re.search(r'Highest degree: ([\S .]+)', msg_dict.get('body')).group(0),
            }
        if re.search(r'UserEnquiry@FindAPhD.com', msg_dict.get('from')).group(0):
            defaults = {
                'name':  re.search(r'Sender\'s First Name: ([\S .]+)', msg_dict.get('body')).group(0) + '' + re.search(r'Sender\'s Last Name: ([\S .]+)', msg_dict.get('body')).group(0),
                'email_from': re.search(r'Sender\'s Email Address: ([\S .]+)', msg_dict.get('body')).group(0),
                'phone': re.search(r'Sender\'s Telephone No.: ([\S .]+)', msg_dict.get('body')).group(0),
            }
        defaults.update(custom_values)
        return super(Lead, self).message_new(msg_dict, custom_values=defaults)
    