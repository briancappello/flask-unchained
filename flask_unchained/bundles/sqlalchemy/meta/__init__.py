"""
This code defers the registration of (some) model classes with SQLAlchemy.
This allows for an external process to decide which model classes it wants
the Mapper to know about. In effect this makes it possible for a vendor
bundle subclass (or the user's app bundle) to extend or override models from
other bundles by defining a new model with the same name. In order for this to
work, a model must declare itself extendable and/or overridable::

    class SomeModel(db.Model):
        class Meta:
            lazy_mapped = True

        # ... (everything else is the same as normal)
"""

from .model_meta_factory import ModelMetaFactory
from .model_meta_options import (
    MetaOption,
    ColumnMetaOption,
    AbstractMetaOption,
    RelationshipsMetaOption,
    PolymorphicMetaOption,
    PolymorphicOnColumnMetaOption,
    PolymorphicIdentityMetaOption,
    PolymorphicBaseTablenameMetaOption,
    PolymorphicJoinedPkColumnMetaOption,
    PrimaryKeyColumnMetaOption,
    CreatedAtColumnMetaOption,
    UpdatedAtColumnMetaOption,
)
from .types import McsArgs
