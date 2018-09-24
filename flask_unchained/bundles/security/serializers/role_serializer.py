try:
    from flask_unchained.bundles.api import ma
except ImportError:
    from py_meta_utils import OptionalClass as ma

from ..models import Role


class RoleSerializer(ma.ModelSerializer):
    """
    Marshmallow serializer for the :class:`Role` model.
    """
    class Meta:
        model = Role
        fields = ('id', 'name')
