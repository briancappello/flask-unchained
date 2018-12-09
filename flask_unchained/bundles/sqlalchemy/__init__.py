from flask_sqlalchemy_unchained import BaseQuery
from flask_unchained import Bundle
from sqlalchemy_unchained import ValidationError, ValidationErrors

from .alembic import MaterializedViewMigration
from .base_model import BaseModel
from .extensions import Migrate, SQLAlchemyUnchained, db, migrate
from .forms import ModelForm, QuerySelectField, QuerySelectMultipleField
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
