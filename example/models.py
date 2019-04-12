import logging
import random

from flask_login import UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy

from example import config
from flask_lti_login.exceptions import ValidationError

logger = logging.getLogger('example.models')

db = SQLAlchemy()
'''
if '@' not in user_id:
 user_id = user_id "@" + tool_consumer_instance_guid

'course': (context_label, context_title, context_id)

query parameter 'next' -> redirect_url
'''


def write_user_to_db(*args, **kwargs):
    logger.info('Signal get:', **kwargs)
    user_id = kwargs['user_id']
    print(user_id)
    user = User.query.filter_by(user_id=user_id).first()

    if user is None:
        print('No such user')
        if not config.CREATE_UNKNOWN_USER:
            return None
            # create new
        user = User(user_id=user_id, email=kwargs['email'], display_name=kwargs['display_name'], sorting_name=kwargs['sorting_name'], is_active=True)
        logger.info('Created a new LTI authenticated user: %s', user)
        db.session.add(user)
    # if exist, update
    user.sorting_name = kwargs['sorting_name']
    user.display_name = kwargs['display_name']
    user.email = kwargs['email']
    # user.is_staff = staff_roles and not roles.isdisjoint(staff_roles) or False
    db.session.commit()
    login_user(user)


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Return a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    return ''.join(random.choice(allowed_chars) for i in range(length))


def word_validator(word, charset, length):
    if charset is not None and not frozenset(word).issubset(charset):
        raise ValidationError(
            "Only following characters are allowed: '{}'"
            .format("".join(charset))
            )
    minlen, maxlen = length
    if len(word) < minlen:
        raise ValidationError("Minimum length is {:d}.".format(minlen))
    if len(word) > maxlen:
        raise ValidationError("Maximum length is {:d}.".format(maxlen))


def create_new_key():
    return get_random_string(
        length=config.KEY_LENGTH,
        allowed_chars=config.BASE_CHARACTERS)


def create_new_secret():
    return get_random_string(
        length=config.SECRET_LENGTH,
        allowed_chars=config.BASE_CHARACTERS)


def key_validator(key):
    return word_validator(key,
                          charset=config.SAFE_CHARACTERS,
                          length=config.KEY_LENGTH_RANGE)


def secret_validator(secret):
    return word_validator(secret,
                          charset=None,
                          length=config.SECRET_LENGTH_RANGE)


"""
Store the LTIClient key/secret
Use "python manage.py add_key" to add a new key/secret pair with empty description
user --key -- secret --description to define the key secret and description
"""


class LTIClient(db.Model):
    key = db.Column(db.String(config.KEY_LENGTH_RANGE[1]), primary_key=True)
    secret = db.Column(db.String(config.SECRET_LENGTH_RANGE[1]))
    description = db.Column(db.Text)


"""
Inherited from the UserMixin in flask_login
'''
Mapping from LTI:
lis_person_name_family -> sorting_name
lis_person_name_full -> full_name
lis_person_name_given -> display_name
lis_person_contact_email_primary -> email

"""


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(config.USER_NAME_LENGTH), unique=True)
    email = db.Column(db.String(config.EMAIL_LENGTH), unique=True, nullable=False)
    display_name = db.Column(db.String(config.FIRST_NAME_LENGTH))
    sorting_name = db.Column(db.String(config.LAST_NAME_LENGTH))
    full_name = db.Column(db.String(config.LAST_NAME_LENGTH + config.FIRST_NAME_LENGTH))
    is_active = db.Column(db.Boolean, default=True)
