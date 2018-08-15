from flask_unchained.bundles.sqlalchemy import db

from flask_unchained.bundles.security.models import Role as BaseRole


class Role(BaseRole):
    description = db.Column(db.Text, nullable=True)
