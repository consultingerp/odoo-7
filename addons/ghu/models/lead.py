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
        body = msg_dict.get('body')
        clean = re.compile('<.*?>')
        if re.search(r'\S+@zapiermail.com', msg_dict.get('from')):
            defaults = {
                'name':  re.search(r'First and Last Name: ([^\t\n\r\f\v<>]*)', body).group(1),
                'email_from': re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body).group(1),
                'phone': re.search(r'Phone Number or Skype: ([^\t\n\r\f\v<>]*)', body).group(1),
                'highest_degree': re.search(r'Highest degree: ([^\t\n\r\f\v<>]*)', body).group(1),
            }
            defaults.update(custom_values)
        if re.search(r'UserEnquiry@FindAPhD.com', msg_dict.get('from')):
            defaults = {
                'name':  re.search(r'Sender\'s First Name: ([^\t\n\r\f\v<>]*)', body).group(1) + '' + re.search(r'Sender\'s Last Name: ([^\t\n\r\f\v<>]*)', body).group(1),
                'email_from': re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body).group(1),
                'phone': re.search(r'Sender\'s Telephone No.: ([^\t\n\r\f\v<>]*)', body).group(1),
            }
            defaults.update(custom_values)
        return super(Lead, self).message_new(msg_dict, custom_values=defaults)

    @api.model
    def message_update(self, msg_dict, update_vals=None):
        if update_vals is None:
            update_vals = {
                'stage_id': 1,
            }
            self.write(update_vals)
        return super(Lead, self).message_update(msg_dict, update_vals=update_vals)
    