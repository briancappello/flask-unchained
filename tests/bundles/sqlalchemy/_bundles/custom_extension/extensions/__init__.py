from sqlalchemy import MetaData

from ..base_model import Model
from .sqlalchemy import SQLAlchemyUnchained


# normally these would go directly in the constructor; this is for testing
kwargs = dict(model_class=Model, metadata=MetaData(naming_convention={
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}))


db = SQLAlchemyUnchained(**kwargs)


EXTENSIONS = {
    'db': db,
}
