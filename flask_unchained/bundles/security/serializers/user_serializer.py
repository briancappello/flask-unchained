try:
    from flask_unchained.bundles.api import ma
except ImportError:
    from py_meta_utils import OptionalClass as ma

from flask_unchained import injectable, lazy_gettext as _

from ..models import User
from ..services import UserManager


class UserSerializer(ma.ModelSerializer):
    """
    Marshmallow serializer for the :class:`User` model.
    """

    user_manager: UserManager = injectable

    email = ma.Email(required=True)
    password = ma.String(required=True)
    roles = ma.Nested('RoleSerializer', only='name', many=True)

    class Meta:
        model = User
        exclude = ('confirmed_at', 'created_at', 'updated_at', 'user_roles')
        dump_only = ('active', 'roles')
        load_only = ('password',)

    @ma.validates('email')
    def validate_email(self, email):
        existing = self.user_manager.get_by(email=email)
        if existing and (self.is_create() or existing != self.instance):
            raise ma.ValidationError(
                _('flask_unchained.bundles.security:error.email_already_associated',
                  email=email))
