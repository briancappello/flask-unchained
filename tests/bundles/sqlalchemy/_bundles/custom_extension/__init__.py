from flask_unchained import unchained
from flask_unchained.bundles.sqlalchemy import SQLAlchemyBundle

from .extensions import db


unchained.extensions.db = db


class CustomSQLAlchemyBundle(SQLAlchemyBundle):
    pass
