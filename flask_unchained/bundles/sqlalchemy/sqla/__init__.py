# alias common names
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

from .column import Column
from .events import attach_events, on, slugify
from .materialized_view import (create_materialized_view,
                                refresh_materialized_view,
                                refresh_all_materialized_views)
from .foreign_key import foreign_key
from .types import BigInteger, DateTime


# a bit of hackery to make type-hinting in PyCharm work correctly
from sqlalchemy.orm.relationships import RelationshipProperty
class _relationship_type_hinter_(RelationshipProperty):
    # implement __call__ to silence PyCharm's "not callable" warning
    def __call__(self, *args, **kwargs):
        pass


def _column_type_hinter_(name=None, type=None, *args, autoincrement='auto',
                         default=None, doc=None, key=None, index=False,
                         info=None, nullable=False, onupdate=None,
                         primary_key=False, server_default=None,
                         server_onupdate=None, quote=None, unique=False,
                         system=False):
    pass
