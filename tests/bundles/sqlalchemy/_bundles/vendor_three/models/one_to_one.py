from flask_unchained.bundles.sqlalchemy import db


class User(db.Model):
    username = db.Column(db.String(64), index=True, unique=True)

    profile_id = db.foreign_key('UserProfile')
    profile = db.relationship('UserProfile', back_populates='user')


class UserProfile(db.Model):
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(64))

    user = db.relationship('User', uselist=False, back_populates='profile')
