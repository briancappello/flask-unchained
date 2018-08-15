from flask import abort
from flask_principal import Permission, RoleNeed
from functools import wraps
from http import HTTPStatus


def roles_required(*roles):
    """
    Decorator which specifies that a user must have all the specified roles.

    Aborts with HTTP 403: Forbidden if the user doesn't have the required roles.

    Example::

        @app.route('/dashboard')
        @roles_required('ROLE_ADMIN', 'ROLE_EDITOR')
        def dashboard():
            return 'Dashboard'

    The current user must have both the `ROLE_ADMIN` and `ROLE_EDITOR` roles
    in order to view the page.

    :param roles: The required roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            perms = [Permission(RoleNeed(role)) for role in roles]
            for perm in perms:
                if not perm.can():
                    abort(HTTPStatus.FORBIDDEN)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
