from flask_sqlalchemy_unchained import BaseQuery
from flask_unchained import Bundle

from .alembic import MaterializedViewMigration
from .base_model import BaseModel
from .extensions import Migrate, SQLAlchemy, db, migrate
from .model_form import ModelForm
from .model_registry import UnchainedModelRegistry
from .services import ModelManager, SessionManager


class SQLAlchemyBundle(Bundle):
    name = 'sqlalchemy_bundle'
    command_group_names = ['db']

    def __init__(self):
        self.models = {}
        """
        A lookup of model classes keyed by class name.
        """

    def after_init_app(self, app):
        UnchainedModelRegistry().finalize_mappings()
