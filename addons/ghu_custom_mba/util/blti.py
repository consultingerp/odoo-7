from lti import ToolConsumer

class GhuBlti():
    
    def createParams(self, key, secret, launch_url, resource_link_id, user_id, lis_person_name_full, lis_person_name_given, lis_person_name_family, lis_person_contact_email_primary):
        params = {}
        params['lti_message_type'] = 'basic-lti-launch-request'
        params['lti_version'] = 'LTI-1p0'
        params['resource_link_id'] = resource_link_id
        params['user_id'] = user_id
        params['lis_person_name_full'] = lis_person_name_full
        params['lis_person_name_given'] = lis_person_name_given
        params['lis_person_name_family'] = lis_person_name_family
        params['lis_person_contact_email_primary'] = lis_person_contact_email_primary
        consumer = ToolConsumer(
            consumer_key=key,
            consumer_secret=secret,
            launch_url=launch_url,
            params=params
        )
        params['launch_data'] = consumer.generate_launch_data()
        params['launch_url'] = consumer.launch_url
        return params