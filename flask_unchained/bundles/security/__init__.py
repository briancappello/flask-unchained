"""
    flask_security_bundle
    ~~~~~~~~~~~~~~~~~~~~~

    Authentication and authorization support for Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.3.0'


from flask_unchained import Bundle

from .decorators import (
    anonymous_user_required,
    auth_required,
    auth_required_same_user,
)
from .models import AnonymousUser, User, Role, UserRole
from .services import SecurityService, UserManager, RoleManager
from .signals import (user_registered, user_confirmed, confirm_instructions_sent,
                      login_instructions_sent, password_reset, password_changed,
                      reset_password_instructions_sent)
from .utils import current_user
from .views import SecurityController, UserResource


class FlaskSecurityBundle(Bundle):
    blueprint_names = []
    command_group_names = ['users', 'roles']
