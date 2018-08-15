from flask_unchained.bundles.sqlalchemy import ModelManager


class RoleManager(ModelManager):
    """
    :class:`ModelManager` for the :class:`Role` model.
    """
    model = 'Role'
