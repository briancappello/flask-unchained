from flask_unchained.bundles.sqlalchemy import ModelManager

from ..models import User


class UserManager(ModelManager):
    """
    :class:`ModelManager` for the :class:`User` model.
    """
    model = User
