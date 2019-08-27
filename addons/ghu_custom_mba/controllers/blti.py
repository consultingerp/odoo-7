from lti import ToolConsumer

class GhuBlti():

    def __init__(self, key, secret, launch_url):
        self.consumer = ToolConsumer(
            consumer_key=key,
            consumer_secret=secret,
            launch_url=launch_url,
        )

    def createParams(self, resource_link_id, user_id, lis_person_name_full, lis_person_name_given, lis_person_name_family, lis_person_contact_email_primary):
        params = {}
        params['lti_message_type'] = 'basic-lti-launch-request'
        params['lti_version'] = 'LTI-1p0'
        params['resource_link_id'] = resource_link_id
        params['user_id'] = user_id
        params['lis_person_name_full'] = lis_person_name_full
        params['lis_person_name_given'] = lis_person_name_given
        params['lis_person_name_family'] = lis_person_name_family
        params['lis_person_contact_email_primary'] = lis_person_contact_email_primary
        self.consumer.params = params
        params['launch_data'] = self.consumer.generate_launch_data()
        params['launch_url'] = self.consumer.launch_url
        return params