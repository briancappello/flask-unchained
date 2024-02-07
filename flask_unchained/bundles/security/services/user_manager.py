from flask_unchained.bundles.sqlalchemy import ModelManager

from ..models import User


class UserManager(ModelManager):
    """
    :class:`~flask_unchained.bundles.sqlalchemy.ModelManager` for the
    :class:`~flask_unchained.bundles.security.User` model.
    """

    class Meta:
        model = User

    def create(self, commit: bool = False, **kwargs) -> User:
        return super().create(commit=commit, **kwargs)
