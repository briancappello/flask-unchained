from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import SQLAlchemyObjectType


class RegisterGrapheneTypesHook(AppFactoryHook):
    name = 'graphene_types'
    bundle_module_name = 'graphql.types'
    run_after = ['models', 'services']

    def process_objects(self,
                        app: FlaskUnchained,
                        types: Dict[str, SQLAlchemyObjectType]):
        self.bundle.types = types

    def type_check(self, obj: Any):
        is_subclass = isinstance(obj, type) and issubclass(obj, SQLAlchemyObjectType)
        return is_subclass and obj != SQLAlchemyObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
