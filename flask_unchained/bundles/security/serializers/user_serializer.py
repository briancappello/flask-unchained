try:
    from flask_unchained.bundles.api import ma
except ImportError:
    from py_meta_utils import OptionalClass as ma

from flask_unchained import injectable

from ..models import User
from ..services import UserManager


class UserSerializer(ma.ModelSerializer):
    """
    Marshmallow serializer for the :class:`User` model.
    """
    email = ma.Email(required=True)
    roles = ma.Nested('RoleSerializer', only='name', many=True)

    class Meta:
        model = User
        exclude = ('confirmed_at', 'created_at', 'updated_at', 'user_roles')
        dump_only = ('active', 'roles')
        load_only = ('password',)

    def __init__(self, *args, user_manager: UserManager = injectable, **kwargs):
        self.user_manager = user_manager
        super().__init__(*args, **kwargs)

    @ma.validates('email')
    def validate_email(self, email):
        existing = self.user_manager.get_by(email=email)
        if existing and (self.is_create() or existing != self.instance):
            raise ma.ValidationError('Sorry, that email is already taken.')
