from flask_unchained.bundles.sqlalchemy import ModelManager

from ..models import Role


class RoleManager(ModelManager):
    """
    :class:`ModelManager` for the :class:`Role` model.
    """
    class Meta:
        model = Role
