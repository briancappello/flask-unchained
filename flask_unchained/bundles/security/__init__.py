from flask_unchained import Bundle

from .decorators import (
    anonymous_user_required,
    auth_required,
    auth_required_same_user,
)
from .models import AnonymousUser, User, Role, UserRole
from .services import SecurityService, SecurityUtilsService, UserManager, RoleManager
from .signals import (user_registered, user_confirmed, confirm_instructions_sent,
                      login_instructions_sent, password_reset, password_changed,
                      reset_password_instructions_sent)
from .utils import current_user
from .views import SecurityController, UserResource
from .extensions import Security, security


class SecurityBundle(Bundle):
    """
    The :class:`Bundle` subclass for the Security Bundle. Has no special behavior.
    """

    blueprint_names = []
    command_group_names = ['users', 'roles']
