from datetime import timedelta
from functools import update_wrapper, wraps

from flask import (abort, current_app, flash, g, make_response, redirect,
                   request)
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required
from rune.util.text import b
from rune.util.url import url_for


def permission_required(permission):
    """Check if the current user, from session, has the permission
    in the argument. """
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.has_permission(permission):
                return f(*args, **kwargs)
            if current_user.has_permission('AUTH-PERMISSION_MISSING'):
                flash(_('Missing permission %(permission)s', permission=b(permission)),
                      'warning')
            abort(403)
        return decorated_function
    return decorator


def api_permission(permission):
    """Check if the current user, from g, has the permission in the argument.
    This is used for API calls, since they don't get stored in the session."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user.has_permission(permission):
                return f(*args, **kwargs)
            abort(403)
        return decorated_function
    return decorator


def role_required(role):
    """Takes a role (a string name of either a role or a permission) and
    returns the function if the user has that role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.has_role(role):  # \
                # or g.current_user.has_role(role):
                return f(*args, **kwargs)
            abort(403)
        return decorated_function
    return decorator


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
        print(headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
