import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from oauthlib.common import urlencode
from oauthlib.oauth1 import SignatureOnlyEndpoint
from flask_login import login_user, current_user
from ltilogin.validators import LTIRequestValidator
from ltilogin.exceptions import PermissionDenied, ValidationError
from ltilogin.login import load_user_from_request
from ltilogin.signals import lti_login_authenticated
from ltilogin import setting

logger = logging.getLogger('flask-ltilogin.lti')

bp = Blueprint('lti', __name__, url_prefix='/lti')


@bp.route('/', methods=['POST'])
def lti():
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
    user_test = load_user_from_request(oauth_request=oauth_request)
    user = current_user
    if not user:
        raise PermissionDenied('Authentication of a LTI request did not yield an user')
    if not user.is_active:
        logger.warning('A LTI login attempt by inactive user: %s', user)
        raise PermissionDenied('An authenticated user is not active')

    # Set vars for listenters
    request.oauth = oauth_request
    oauth_request.redirect_url = setting.LOGIN_REDIRECT_URL
    oauth_request.set_cookies = []

    #send signal
    #TODO
    #login use into session
    login_user(user)
    flash('Logged in successfully.')
    response = redirect(oauth_request.redirect_url)

    for args, kwargs in oauth_request.set_cookies:
        response.set_cookie(*args, **kwargs)

    logger.debug('Login completed for a LTI authenticated user: %s', user)
    return response