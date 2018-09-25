from flask_unchained.bundles.sqlalchemy import db

from .user_role import UserRole


class Role(db.Model):
    """
    Base :class`Role` model. Includes an :attr:`name` column and a many-to-many
    relationship with the :class:`User` model via the intermediary :class:`UserRole`
    join table.
    """
    class Meta:
        lazy_mapped = True
        repr = ('id', 'name')

    name = db.Column(db.String(64), unique=True, index=True)

    role_users = db.relationship('UserRole', back_populates='role',
                                 cascade='all, delete-orphan')
    users = db.association_proxy('role_users', 'user',
                                 creator=lambda user: UserRole(user=user))

    def __hash__(self):
        return hash(self.name)
