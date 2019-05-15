import logging

from flask import current_app
from flask_login import LoginManager

from flask_lti_login.models import User

login_manager = LoginManager()
logger = logging.getLogger('ltilogin.login')


def check_user_id(user_id, guid):
    return user_id if '@' in user_id else user_id + "@" + guid


def load_user_from_request(oauth_request):
    body = oauth_request.body
    if not oauth_request:
        logger.warning('No request')
        return None
    try:
        user_id = body['user_id'][:current_app.config['USER_NAME_LENGTH']]
    except KeyError:
        logger.warning('LTI login attempt without a user id.')
        return None

    accepted_roles = None
    staff_roles = None
    # get parameters and truncate to lengths that can be stored into database
    email = body['lis_person_contact_email_primary'][:current_app.config['EMAIL_LENGTH']] or ''
    display_name = body['lis_person_name_given'][:current_app.config['FIRST_NAME_LENGTH']] or ''
    sorting_name = body['lis_person_name_family'][:current_app.config['LAST_NAME_LENGTH']] or ''
    full_name = body['lis_person_name_full'][
                :(current_app.config['FIRST_NAME_LENGTH'] + current_app.config['LAST_NAME_LENGTH'])] or ' '
    roles = body['roles'] if oauth_request.body['roles'] else None
    # if accepted_roles and roles.isdisjoint(accepted_roles):
    #     logger.warning('LTI login attempt without accepted user role: %s', roles)
    #     return None
    # Retrieve user information
    user = User(
        user_id=check_user_id(user_id, body['tool_consumer_instance_guid']),
        email=email,
        display_name=display_name,
        sorting_name=sorting_name,
        full_name=full_name,
        roles=roles
    )
    # user.is_staff = staff_roles and not roles.isdisjoint(staff_roles) or False
    logger.info('LTI authentication accepted for: %s', user)
    oauth_request.redirect_url = current_app.config['LOGIN_REDIRECT_URL']
    # oauth_request.set_cookies = []
    return user
