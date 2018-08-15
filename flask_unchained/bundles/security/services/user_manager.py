from flask_unchained.bundles.sqlalchemy import ModelManager


class UserManager(ModelManager):
    """
    :class:`ModelManager` for the :class:`User` model.
    """
    model = 'User'
