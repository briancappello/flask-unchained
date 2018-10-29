import inspect

from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import MutationObjectType


class RegisterGrapheneMutationsHook(AppFactoryHook):
    name = 'graphene_mutations'
    bundle_module_name = 'graphql.schema'
    run_after = ['graphene_types']

    def process_objects(self,
                        app: FlaskUnchained,
                        mutations: Dict[str, MutationObjectType]):
        self.bundle.mutations = mutations

    def type_check(self, obj: Any):
        is_subclass = inspect.isclass(obj) and issubclass(obj, MutationObjectType)
        return is_subclass and obj != MutationObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
