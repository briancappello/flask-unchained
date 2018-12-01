from .migrate import Migrate
from .sqlalchemy import SQLAlchemyUnchained


db = SQLAlchemyUnchained()
migrate = Migrate()


EXTENSIONS = {
    'db': db,
    'migrate': (migrate, ['db']),
}


__all__ = [
    'db',
    'SQLAlchemyUnchained',
    'migrate',
    'Migrate',
]
