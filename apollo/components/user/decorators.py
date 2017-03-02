
import base64
from functools import wraps
from flask import request, jsonify, make_response
from google.appengine.ext import ndb

from .models import User


def deco_auth_user(username, email, password):
    """
    deco_auth_user to be used in tests, it will create a user and token
    :param username:
    :param email:
    :param password:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if getattr(args[0], 'users', None) is None:
                setattr(args[0], 'users', [])
            user = User.create(email=email, username=username, password=password)
            # token = user.generate_auth_token(expiration=600)
            # headers = dict()
            # headers['AUTHORIZATION'] = ('Bearer %s' % token)
            # setattr(user, 'headers', headers)
            setattr(args[0], username, user)
            args[0].users.append(user)
            return func(*args, **kwargs)
        return func_wrapper
    return decorator
