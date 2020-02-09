from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import SQLAlchemyObjectType


class RegisterGrapheneTypesHook(AppFactoryHook):
    """
    Registers SQLAlchemyObjectTypes with the Graphene Bundle.
    """

    name = 'graphene_types'
    """
    The name of this hook.
    """

    bundle_module_names = ['graphene.types', 'graphene.schema']
    """
    The default module this hook loads from.

    Override by setting the ``graphene_types_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'graphene_types_module_names'
    run_after = ['models', 'services']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        types: Dict[str, SQLAlchemyObjectType]):
        self.bundle.types = types

    def type_check(self, obj: Any):
        is_subclass = isinstance(obj, type) and issubclass(obj, SQLAlchemyObjectType)
        return is_subclass and obj != SQLAlchemyObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
