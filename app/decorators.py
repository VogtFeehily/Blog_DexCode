# coding=utf-8
from functools import wraps
from flask import abort
from flask_login import current_user


def dexter_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = current_user
        if not user.is_dexter():
            abort(403)
        return func(*args, **kwargs)
    return decorated_function
