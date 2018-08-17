from flask import abort, request
from flask_principal import Permission, UserNeed
from functools import wraps
from http import HTTPStatus

from .auth_required import auth_required


def auth_required_same_user(*args, **kwargs):
    """
    Decorator for requiring an authenticated user to be the same as the
    user in the URL parameters. By default the user url parameter name to
    lookup is ``id``, but this can be customized by passing an argument::

        @auth_require_same_user('user_id')
        @bp.route('/users/<int:user_id>/foo/<int:id>')
        def get(user_id, id):
            # do stuff

    Any keyword arguments are passed along to the @auth_required decorator,
    so roles can also be specified in the same was as it, eg::

        @auth_required_same_user('user_id', role='ROLE_ADMIN')

    Aborts with ``HTTP 403: Forbidden`` if the user-check fails.
    """
    auth_kwargs = {}
    user_id_parameter_name = 'id'
    if not (args and callable(args[0])):
        auth_kwargs = kwargs
        if args and isinstance(args[0], str):
            user_id_parameter_name = args[0]

    def wrapper(fn):
        @wraps(fn)
        @auth_required(**auth_kwargs)
        def decorated(*args, **kwargs):
            try:
                user_id = request.view_args[user_id_parameter_name]
            except KeyError:
                raise KeyError('Unable to find the user lookup parameter '
                               f'{user_id_parameter_name} in the url args')
            if not Permission(UserNeed(user_id)).can():
                abort(HTTPStatus.FORBIDDEN)
            return fn(*args, **kwargs)
        return decorated

    if args and callable(args[0]):
        return wrapper(args[0])
    return wrapper
