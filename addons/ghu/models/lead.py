from odoo import fields, models, api
import re
import requests
import json

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


    @api.model
    def _import_keystone_custom_mba(self):
        url = "https://smarthub.keystoneacademic.com/api/rest/getLead"
        payload = {"programs": [129181], "after": "2019-09-24"}
        headers = {
            'x-api-key': self.env['ir.config_parameter'].sudo().get_param('ghu.smarthub_api_key'),
            'cache-control': "no-cache"
            }

        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code != 200:
            # This means something went wrong.
            print('oh no')
        else:
            leads = response.json()
            leadsToImport = []

            sales_team = self.env['crm.team'].search([('name','ilike','Smarthub')], limit=1)
            study_id = self.env['ghu.study'].search([('code','=','CMBA')], limit=1).id
            for lead in leads['data']:
                if self.env['crm.lead'].search([('reveal_id', '=', lead['id'])]):
                    print('Lead {} {} already exists'.format(lead['id'], lead['firstname']))
                    continue
                lead = {
                    'reveal_id': lead['id'],
                    'name': lead['firstname'] + ' ' + lead['lastname'],
                    'highest_degree': lead['highest_degree'],
                    'nationality': self.env['res.country'].search([('code','=',lead['contact']['nationality_country']['iso_3166_1_alpha_2'])], limit=1).id,
                    'study_id': study_id,
                    'email_from': lead['contact']['email'],
                    'phone': lead['contact']['phone'],
                    'team_id': sales_team.id,
                    'user_id': sales_team.user_id.id,
                    'stage_id': 1,
                    'type': 'opportunity',
                    'description': lead['comment']
                }
                leadsToImport.append(lead)
            self.env['crm.lead'].create(leadsToImport)
    
    @api.model
    def _import_keystone_doctoral(self):
        url = "https://smarthub.keystoneacademic.com/api/rest/getLead"
        payload = {"programs": [129183, 129182], "after": "2019-10-02"}
        headers = {
            'x-api-key': self.env['ir.config_parameter'].sudo().get_param('ghu.smarthub_api_key'),
            'cache-control': "no-cache"
            }

        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code != 200:
            # This means something went wrong.
            print('oh no')
        else:
            leads = response.json()
            leadsToImport = []

            sales_team = self.env['crm.team'].search([('name','ilike','Smarthub')], limit=1)
            
            for lead in leads['data']:
                if self.env['crm.lead'].search([('reveal_id', '=', lead['id'])]):
                    print('Lead {} {} already exists'.format(lead['id'], lead['firstname']))
                    continue
                lead = {
                    'reveal_id': lead['id'],
                    'name': lead['firstname'] + ' ' + lead['lastname'],
                    'highest_degree': lead['highest_degree'],
                    'nationality': self.env['res.country'].search([('code','=',lead['contact']['nationality_country']['iso_3166_1_alpha_2'])], limit=1).id,
                    'email_from': lead['contact']['email'],
                    'phone': lead['contact']['phone'],
                    'team_id': sales_team.id,
                    'user_id': sales_team.user_id.id,
                    'stage_id': 1,
                    'type': 'opportunity',
                    'description': str(lead['comment']) + '\nProgram: ' + str(lead['program']['name'])
                }
                leadsToImport.append(lead)
            self.env['crm.lead'].create(leadsToImport)
    




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
        defaults = {}
        if re.search(r'\S+@zapiermail.com', msg_dict.get('from')):
            defaults = {
                'name':  re.search(r'First and Last Name: ([^\t\n\r\f\v<>]*)', body).group(1),
                'email_from': re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body).group(1),
                'phone': re.search(r'Phone Number or Skype: ([^\t\n\r\f\v<>]*)', body).group(1),
                'highest_degree': re.search(r'Highest degree: ([^\t\n\r\f\v<>]*)', body).group(1),
            }
            defaults.update(custom_values)
        if re.search(r'UserEnquiry@FindAPhD.com', msg_dict.get('from')):
            firstNameRegex = re.search(r'Sender\'s First Name: ([^\t\n\r\f\v<>]*)', body)
            lastNameRegex = re.search(r'Sender\'s Last Name: ([^\t\n\r\f\v<>]*)', body)
            mailRegex = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body)
            phoneRegex = re.search(r'Sender\'s Telephone No.: ([^\t\n\r\f\v<>]*)', body)
            firstName = firstNameRegex.group(1) if firstNameRegex is not None else ''
            lastName = lastNameRegex.group(1) if lastNameRegex is not None else ''
            mail = mailRegex.group(1) if mailRegex is not None else ''
            phone = phoneRegex.group(1) if phoneRegex is not None else ''
            defaults = {
                'name':  firstName + ' ' + lastName,
                'email_from': mail,
                'phone': phone,
            }
            defaults.update(custom_values)
        if re.search(r'UserEnquiry@FindAMasters.com', msg_dict.get('from')):
            firstNameRegex = re.search(r'Sender\'s First Name: ([^\t\n\r\f\v<>]*)', body)
            lastNameRegex = re.search(r'Sender\'s Last Name: ([^\t\n\r\f\v<>]*)', body)
            mailRegex = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body)
            phoneRegex = re.search(r'Sender\'s Telephone No.: ([^\t\n\r\f\v<>]*)', body)
            firstName = firstNameRegex.group(1) if firstNameRegex is not None else ''
            lastName = lastNameRegex.group(1) if lastNameRegex is not None else ''
            mail = mailRegex.group(1) if mailRegex is not None else ''
            phone = phoneRegex.group(1) if phoneRegex is not None else ''
            defaults = {
                'name':  firstName + ' ' + lastName,
                'email_from': mail,
                'phone': phone,
            }
            defaults.update(custom_values)
        if re.search(r'UserEnquiry@FindAnMBA.com', msg_dict.get('from')):
            firstNameRegex = re.search(r'Sender\'s First Name: ([^\t\n\r\f\v<>]*)', body)
            lastNameRegex = re.search(r'Sender\'s Last Name: ([^\t\n\r\f\v<>]*)', body)
            mailRegex = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', body)
            phoneRegex = re.search(r'Sender\'s Telephone No.: ([^\t\n\r\f\v<>]*)', body)
            firstName = firstNameRegex.group(1) if firstNameRegex is not None else ''
            lastName = lastNameRegex.group(1) if lastNameRegex is not None else ''
            mail = mailRegex.group(1) if mailRegex is not None else ''
            phone = phoneRegex.group(1) if phoneRegex is not None else ''
            defaults = {
                'name':  firstName + ' ' + lastName,
                'email_from': mail,
                'phone': phone,
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
    
