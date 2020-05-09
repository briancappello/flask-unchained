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
    """
    The SQLAlchemy Bundle. Integrates `SQLAlchemy <https://www.sqlalchemy.org/>`_
    and `Flask-Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_
    with Flask Unchained.
    """

    name = 'sqlalchemy_bundle'
    """
    The name of the SQLAlchemy Bundle.
    """

    command_group_names = ['db']
    """
    Click groups for the SQLAlchemy Bundle.
    """

    _has_views = False

    def __init__(self):
        self.models = {}
        """
        A lookup of model classes keyed by class name.
        """
