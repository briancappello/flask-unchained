from flask import _request_ctx_stack, current_app, request
from flask_principal import Identity, identity_changed
from flask_unchained import unchained
from functools import wraps

from .roles_accepted import roles_accepted
from .roles_required import roles_required
from ..utils import current_user

security = unchained.get_local_proxy('security')


def auth_required(decorated_fn=None, **role_rules):
    """
    Decorator for requiring an authenticated user, optionally with roles.

    Roles are passed as keyword arguments, like so::

        @auth_required(role='REQUIRE_THIS_ONE_ROLE')
        @auth_required(roles=['REQUIRE', 'ALL', 'OF', 'THESE', 'ROLES'])
        @auth_required(one_of=['EITHER_THIS_ROLE', 'OR_THIS_ONE'])

    One of role or roles kwargs can also be combined with one_of::

        @auth_required(role='REQUIRED', one_of=['THIS', 'OR_THIS'])

    Aborts with ``HTTP 401: Unauthorized`` if no user is logged in, or
    ``HTTP 403: Forbidden`` if any of the specified role checks fail.
    """
    required_roles = []
    one_of_roles = []
    if not (decorated_fn and callable(decorated_fn)):
        if 'role' in role_rules and 'roles' in role_rules:
            raise RuntimeError('specify only one of `role` or `roles` kwargs')
        elif 'role' in role_rules:
            required_roles = [role_rules['role']]
        elif 'roles' in role_rules:
            required_roles = role_rules['roles']

        if 'one_of' in role_rules:
            one_of_roles = role_rules['one_of']

    def wrapper(fn):
        @wraps(fn)
        @_auth_required()
        @roles_required(*required_roles)
        @roles_accepted(*one_of_roles)
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorated

    if decorated_fn and callable(decorated_fn):
        return wrapper(decorated_fn)
    return wrapper


def _auth_required():
    """
    Decorator that protects endpoints through token and session auth mechanisms
    """

    login_mechanisms = (
        ('token', lambda: _check_token()),
        ('session', lambda: current_user.is_authenticated),
    )

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            for method, mechanism in login_mechanisms:
                if mechanism and mechanism():
                    return fn(*args, **kwargs)
            return security._unauthorized_callback()
        return decorated_view
    return wrapper


def _check_token():
    user = security.login_manager.request_callback(request)

    if user and user.is_authenticated:
        _request_ctx_stack.top.user = user
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))
        return True

    return False
