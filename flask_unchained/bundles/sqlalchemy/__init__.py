"""
    flask_unchained.bundles.sqlalchemy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds SQLAlchemy and Alembic to Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.3.2'


from flask_unchained import Bundle

from .alembic import MaterializedViewMigration
from .base_model import BaseModel
from .base_query import BaseQuery
from .decorators import param_converter
from .extensions import SQLAlchemy, db
from .model_form import ModelForm
from .services import ModelManager, SessionManager
from .validation import (
    BaseValidator, Required, ValidationError, ValidationErrors, validates)


class SQLAlchemyBundle(Bundle):
    name = 'sqlalchemy_bundle'
    command_group_names = ['db']

    @classmethod
    def after_init_app(cls, app):
        from .meta.model_registry import _model_registry
        _model_registry.finalize_mappings()
