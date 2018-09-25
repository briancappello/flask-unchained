"""
The code in this module allows the ability to defer the registration of model classes
with SQLAlchemy. This allows for us to decide which model classes we want the
SQLAlchemy :class:`~sqlalchemy.orm.mapper.Mapper` to know about. In effect this
makes it possible for the user's app bundle (or a vendor bundle subclass) to extend
or override models from other bundles by defining a new model with the same name.
In order for this to work, a model must declare itself as extendable/overridable
by setting ``Meta.lazy_mapped`` to ``True``::

    class SomeModel(db.Model):
        class Meta:
            lazy_mapped = True

        # ... (everything else is the same as normal)
"""
from .base_model_metaclass import BaseModelMetaclass
from .model_meta_options_factory import ModelMetaOptionsFactory
from .model_registry import ModelRegistry
