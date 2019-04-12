from collections import namedtuple


'''
Mapping from LTI:
lis_person_name_family -> sorting
lis_person_name_full -> full_name
lis_person_name_given -> display_name
lis_person_contact_email_primary -> email

if '@' not in user_id:
 user_id = user_id "@" + tool_consumer_instance_guid

'course': (context_label, context_title, context_id)

query parameter 'next' -> redirect_url
'''
User = namedtuple('User', ['user_id', 'full_name', 'display_name', 'sorting_name', 'email', 'guid'])
