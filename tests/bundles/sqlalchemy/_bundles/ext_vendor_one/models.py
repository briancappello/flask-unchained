from flask_unchained.bundles.sqlalchemy import db


from ..vendor_one.models import OneBasic as BaseOneBasic


# test extending OneBasic to add an extra column
class OneBasic(BaseOneBasic):
    class Meta:
        lazy_mapped = True

    ext = db.Column(db.String)


# test overriding OneParent to remove the children relationship
class OneParent(db.Model):
    class Meta:
        lazy_mapped = True

    name = db.Column(db.String)


# test overriding OneUser and OneRole to change the roles relationship to be
# one-to-many instead of many-to-many
class OneUser(db.Model):
    class Meta:
        lazy_mapped = True

    name = db.Column(db.String)

    roles = db.relationship('OneRole', back_populates='user')


class OneRole(db.Model):
    class Meta:
        lazy_mapped = True

    name = db.Column(db.String)

    user_id = db.foreign_key('OneUser')
    user = db.relationship('OneUser', back_populates='roles')
