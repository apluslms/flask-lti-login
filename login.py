import logging
from flask_login import LoginManager
from .models import User
from .setting import CREATE_UNKNOWN_USER, LAST_NAME_LENGTH,\
     EMAIL_LENGTH, FIRST_NAME_LENGTH, USER_NAME_LENGTH


login_manager = LoginManager()
logger = logging.getLogger('django_lti_login.backends')


@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user


@login_manager.request_loader
def load_user_from_request(oauth_request):
    if not oauth_request:
        return None
    if not oauth_request.user_id:
        logger.warning('LTI login attempt without a user id.')
        return None
        username_field = getattr(User, 'user_name', 'username')
        accepted_roles = None
        staff_roles = None

        # get parameters and truncate to lengths that can be stored into database
        username = oauth_request.user_id[:USER_NAME_LENGTH]
        email = oauth_request.lis_person_contact_email_primary[:EMAIL_LENGTH] or ''
        first_name = oauth_request.lis_person_name_given[:FIRST_NAME_LENGTH] or ''
        last_name = oauth_request.lis_person_name_family[:LAST_NAME_LENGTH] or ''
        roles = frozenset(oauth_request.roles.split(',')) if oauth_request.roles else frozenset()

        if accepted_roles and roles.isdisjoint(accepted_roles):
            logger.warning('LTI login attempt without accepted user role: %s', roles)
            return None

        try:
            # get
            user = UserModel.objects.get(**{username_field: username})
            # update
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
        except UserModel.DoesNotExist:
            if not CREATE_UNKNOWN_USER:
                return None

            # create new
            user = UserModel.objects.create_user(username, email, first_name=first_name, last_name=last_name)
            user.set_unusable_password()
            logger.info('Created a new LTI authenticated user: %s', user)

        user.is_staff = staff_roles and not roles.isdisjoint(staff_roles) or False
        user.save()

        logger.info('LTI authentication accepted for: %s', user)
        return user
