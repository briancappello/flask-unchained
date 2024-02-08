from flask_unchained import Bundle

from .decorators import anonymous_user_required, auth_required, auth_required_same_user
from .exceptions import AuthenticationError, SecurityException
from .models import AnonymousUser, Role, User, UserRole
from .services import RoleManager, SecurityService, SecurityUtilsService, UserManager
from .utils import current_user
from .views import SecurityController, UserResource


from .extensions import Security, security  # isort: skip (must be last)


class SecurityBundle(Bundle):
    """
    The Security Bundle. Integrates
    `Flask Login <https://flask-login.readthedocs.io/en/latest/>`_ and
    `Flask Principal <https://pythonhosted.org/Flask-Principal/>`_
    with Flask Unchained.
    """

    name = "security_bundle"
    """
    The name of the Security Bundle.
    """

    dependencies = (
        "flask_unchained.bundles.controller",
        "flask_unchained.bundles.session",
        "flask_unchained.bundles.sqlalchemy",
        "flask_unchained.bundles.babel",
    )

    command_group_names = ["users", "roles"]
    """
    Click groups for the Security Bundle.
    """
