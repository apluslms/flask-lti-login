import logging
from flask_login import LoginManager
from ltilogin.models import User, db
from ltilogin import setting

login_manager = LoginManager()
logger = logging.getLogger('flask-ltilogin.login')


@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user


@login_manager.request_loader
def load_user_from_request(oauth_request):
    if not oauth_request:
        return None
    if not hasattr(oauth_request, 'user_id'):
        logger.warning('LTI login attempt without a user id.')
        return None

        accepted_roles = None
        staff_roles = None

        # get parameters and truncate to lengths that can be stored into database
        username = oauth_request.user_id[:setting.USER_NAME_LENGTH]
        email = oauth_request.lis_person_contact_email_primary[:setting.EMAIL_LENGTH] or ''
        first_name = oauth_request.lis_person_name_given[:setting.FIRST_NAME_LENGTH] or ''
        last_name = oauth_request.lis_person_name_family[:setting.LAST_NAME_LENGTH] or ''
        roles = frozenset(oauth_request.roles.split(',')) if oauth_request.roles else frozenset()

        if accepted_roles and roles.isdisjoint(accepted_roles):
            logger.warning('LTI login attempt without accepted user role: %s', roles)
            return None


        # get
        user = User.query.filter_by(username=username)
        if user is None:
            if not setting.CREATE_UNKNOWN_USER:
                return None
            # create new
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()
            logger.info('Created a new LTI authenticated user: %s', user)
        # if exist, update
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = staff_roles and not roles.isdisjoint(staff_roles) or False
        user.save()
        logger.info('LTI authentication accepted for: %s', user)
        return user