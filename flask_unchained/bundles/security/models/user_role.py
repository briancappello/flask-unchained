from flask_unchained.bundles.sqlalchemy import db


class UserRole(db.Model):
    """
    Join table between the :class:`User` and :class:`Role` models.
    """
    class Meta:
        lazy_mapped = True
        pk = None

    user_id = db.foreign_key('User', primary_key=True)
    user = db.relationship('User', back_populates='user_roles')

    role_id = db.foreign_key('Role', primary_key=True)
    role = db.relationship('Role', back_populates='role_users')

    __repr_props__ = ('user_id', 'role_id')

    def __init__(self, user=None, role=None, **kwargs):
        super().__init__(**kwargs)
        if user:
            self.user = user
        if role:
            self.role = role
