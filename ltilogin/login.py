import logging
from flask_login import LoginManager
from ltilogin.models import User, db
from ltilogin import setting
from oauthlib.common import urlencode
from oauthlib.oauth1 import SignatureOnlyEndpoint
from ltilogin.validators import LTIRequestValidator
from ltilogin.exceptions import PermissionDenied, ValidationError
from ltilogin import setting


login_manager = LoginManager()
logger = logging.getLogger('flask-ltilogin.login')


@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user

@login_manager.request_loader
def load_user_from_request(request):
    uri = request.base_url
    headers = dict(request.headers)
    method = request.method
    body = request.form
    if 'HTTP_AUTHORIZATION' in headers:
        headers['Authorization'] = headers['HTTP_AUTHORIZATION']
    if 'CONTENT_TYPE' in headers:
        headers['Content-Type'] = headers['CONTENT_TYPE']

    # create oauth endpoint and validate request
    endpoint = SignatureOnlyEndpoint(LTIRequestValidator())
    is_valid, oauth_request = endpoint.validate_request(uri, method, body, headers) 

    if not is_valid:
        logger.warning('An invalid LTI login request. Are the tokens configured correctly?')
        raise PermissionDenied('An invalid LTI login request. Are the tokens configured correctly?')

    if (oauth_request.lti_version != 'LTI-1p0' or
        oauth_request.lti_message_type != 'basic-lti-launch-request'):
        logger.warning('A LTI login request is not LTI-1p0 or basic-lti-launch-request.')
        raise PermissionDenied('Version is not LTI-1p0 or type is not basic-lti-launch-request for a LTI login request.')
    """ 
    Load user from the request, store in current_user global object
     """
    body = oauth_request.body
    print(body)
    if not oauth_request:
        logger.Warning('No request')
        return None
    try:
        username = body['user_id'][:setting.USER_NAME_LENGTH]
    except KeyError:
        logger.warning('LTI login attempt without a user id.')
        return None

    accepted_roles = None
    staff_roles = None
        # get parameters and truncate to lengths that can be stored into database
    email = body['lis_person_contact_email_primary'][:setting.EMAIL_LENGTH] or ''
    first_name = body['lis_person_name_given'][:setting.FIRST_NAME_LENGTH] or ''
    last_name = body['lis_person_name_family'][:setting.LAST_NAME_LENGTH] or ''
    roles = frozenset(body['roles'].split(',')) if oauth_request.body['roles'] else frozenset()
    print(username, email, first_name, last_name, roles)
    if accepted_roles and roles.isdisjoint(accepted_roles):
        logger.warning('LTI login attempt without accepted user role: %s', roles)
        return None
        # get
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        if not setting.CREATE_UNKNOWN_USER:
            return None
            # create new
        user = User(username=username, email=email, first_name=first_name, last_name=last_name, is_active=True)

        logger.info('Created a new LTI authenticated user: %s', user)
        # if exist, update
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.is_staff = staff_roles and not roles.isdisjoint(staff_roles) or False
    db.session.add(user)
    db.session.commit()
    logger.info('LTI authentication accepted for: %s', user)
    oauth_request.redirect_url = setting.LOGIN_REDIRECT_URL
    # oauth_request.set_cookies = []
    return user
