from flask_unchained import Bundle

from .decorators import anonymous_user_required, auth_required, auth_required_same_user
from .exceptions import SecurityException, AuthenticationError
from .models import AnonymousUser, User, Role, UserRole
from .services import SecurityService, SecurityUtilsService, UserManager, RoleManager
from .utils import current_user
from .views import SecurityController, UserResource
from .extensions import Security, security  # must be imported last


class SecurityBundle(Bundle):
    """
    The Security Bundle. Integrates
    `Flask Login <https://flask-login.readthedocs.io/en/latest/>`_ and
    `Flask Principal <https://pythonhosted.org/Flask-Principal/>`_
    with Flask Unchained.
    """

    name = 'security_bundle'
    """
    The name of the Security Bundle.
    """

    command_group_names = ['users', 'roles']
    """
    Click groups for the Security Bundle.
    """
