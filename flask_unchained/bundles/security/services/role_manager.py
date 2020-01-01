from flask_unchained.bundles.sqlalchemy import ModelManager

from ..models import Role


class RoleManager(ModelManager):
    """
    :class:`~flask_unchained.bundles.sqlalchemy.ModelManager` for the
    :class:`~flask_unchained.bundles.security.Role` model.
    """
    class Meta:
        model = Role
