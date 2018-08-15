from flask_unchained.bundles.security.models import User as BaseUser
from flask_unchained.bundles.sqlalchemy import db


class User(BaseUser):
    username = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
