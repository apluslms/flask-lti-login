from .validators import LTIRequestValidator
from .exceptions import PermissionDenied
from .login import load_user_from_request
from .signals import lti_login_authenticated
import logging

from flask import (
    Blueprint, flash, redirect, request,
    current_app)
from oauthlib.oauth1 import SignatureOnlyEndpoint

lti = Blueprint('lti', __name__, url_prefix='/lti')

logger = logging.getLogger('flask_lti_login.views')


@lti.route('/', methods=['POST'])
def lti_login():
    uri = request.base_url
    headers = dict(request.headers)
    method = request.method
    body = request.form
    endpoint = SignatureOnlyEndpoint(LTIRequestValidator())
    is_valid, oauth_request = endpoint.validate_request(uri, method, body, headers)
    if not is_valid:
        logger.warning('An invalid LTI login request. Are the tokens configured correctly?')
        raise PermissionDenied('An invalid LTI login request. Are the tokens configured correctly?')

    user = load_user_from_request(oauth_request)
    if not user:
        raise PermissionDenied('Authentication of a LTI request did not yield an user')
    # if not user.is_active:
    #     logger.warning('A LTI login attempt by inactive user: %s', user)
    #     raise PermissionDenied('An authenticated user is not active')

    # Set vars for listenters
    # request.oauth = oauth_request
    oauth_request.redirect_url = current_app.config['LOGIN_REDIRECT_URL']
    oauth_request.set_cookies = []

    # send signal
    lti_login_authenticated.send(**dict(user._asdict()))

    flash('Logged in successfully.')
    response = redirect(current_app.config['LOGIN_REDIRECT_URL'])

    for args, kwargs in oauth_request.set_cookies:
        response.set_cookie(*args, **kwargs)

    logger.debug('Login completed for a LTI authenticated user: %s', user)
    return response