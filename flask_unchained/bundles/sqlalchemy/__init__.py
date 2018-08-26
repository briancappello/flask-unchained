from flask_unchained import Bundle

from .alembic import MaterializedViewMigration
from .base_model import BaseModel
from .base_query import BaseQuery
from .extensions import Migrate, SQLAlchemy, db, migrate
from .model_form import ModelForm
from .services import ModelManager, SessionManager
from .validation import (
    BaseValidator, Required, ValidationError, ValidationErrors, validates)


class SQLAlchemyBundle(Bundle):
    name = 'sqlalchemy_bundle'
    command_group_names = ['db']

    def __init__(self):
        self.models = {}
        """
        A lookup of model classes keyed by class name.
        """

    def after_init_app(self, app):
        from .meta.model_registry import _model_registry
        _model_registry.finalize_mappings()
