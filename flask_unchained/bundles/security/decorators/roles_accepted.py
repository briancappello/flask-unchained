from flask import abort
from flask_principal import Permission, RoleNeed
from functools import wraps
from http import HTTPStatus


def roles_accepted(*roles):
    """
    Decorator which specifies that a user must have at least one of the
    specified roles.

    Aborts with HTTP: 403 if the user doesn't have at least one of the roles.

    Example::

        @app.route('/create_post')
        @roles_accepted('ROLE_ADMIN', 'ROLE_EDITOR')
        def create_post():
            return 'Create Post'

    The current user must have either the `ROLE_ADMIN` role or `ROLE_EDITOR`
    role in order to view the page.

    :param roles: The possible roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            perm = Permission(*[RoleNeed(role) for role in roles])
            if not perm.can():
                abort(HTTPStatus.FORBIDDEN)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
