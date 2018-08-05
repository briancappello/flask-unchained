"""
    SQLAlchemy Bundle
    -----------------

    Adds SQLAlchemy and Alembic to Flask Unchained
"""

from flask_unchained import Bundle
from flask_unchained.utils import AttrDict

from .alembic import MaterializedViewMigration
from .base_model import BaseModel
from .base_query import BaseQuery
from .extensions import SQLAlchemy, db
from .model_form import ModelForm
from .services import ModelManager, SessionManager
from .validation import (
    BaseValidator, Required, ValidationError, ValidationErrors, validates)


class SQLAlchemyBundle(Bundle):
    name = 'sqlalchemy_bundle'
    command_group_names = ['db']

    store = AttrDict(
        # model class name -> model class
        models={},
    )

    @classmethod
    def after_init_app(cls, app):
        from .meta.model_registry import _model_registry
        _model_registry.finalize_mappings()
