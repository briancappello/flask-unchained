from flask_unchained.bundles.security.models import Role as BaseRole
from flask_unchained.bundles.sqlalchemy import db


class Role(BaseRole):
    description = db.Column(db.Text, nullable=True)
