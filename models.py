from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .setting import KEY_LENGTH, KEY_LENGTH_RANGE, SECRET_LENGTH, \
    BASE_CHARACTERS, SAFE_CHARACTERS, SECRET_LENGTH_RANGE, EMAIL_LENGTH, \
    LAST_NAME_LENGTH, FIRST_NAME_LENGTH, USER_NAME_LENGTH
from .exceptions import ValidationError

import random

db = SQLAlchemy()


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
        length=KEY_LENGTH,
        allowed_chars=BASE_CHARACTERS)


def create_new_secret():
    return get_random_string(
        length=SECRET_LENGTH,
        allowed_chars=BASE_CHARACTERS)


def key_validator(key):
    return word_validator(key,
                          charset=SAFE_CHARACTERS,
                          length=KEY_LENGTH)


def secret_validator(secret):
    return word_validator(secret,
                          charset=None,
                          length=SECRET_LENGTH)


class LTIClient(db.Model):
    key = db.Column(db.String(KEY_LENGTH_RANGE[1]), primary_key=True)
    secret = db.Column(db.String(SECRET_LENGTH_RANGE[1]))
    description = db.Column(db.Text)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USER_NAME_LENGTH), unique=True, nullable=False)
    email = db.Column(db.String(EMAIL_LENGTH), unique=True, nullable=False)
    first_name = db.Column(db.String(FIRST_NAME_LENGTH))
    last_name= db.Column(db.String(LAST_NAME_LENGTH))
    is_active = db.Column(db.Boolean, default=False)
