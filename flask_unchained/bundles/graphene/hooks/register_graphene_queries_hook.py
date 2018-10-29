import inspect

from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import QueryObjectType


class RegisterGrapheneQueriesHook(AppFactoryHook):
    name = 'graphene_queries'
    bundle_module_name = 'graphql.schema'
    run_after = ['graphene_types']

    def process_objects(self,
                        app: FlaskUnchained,
                        queries: Dict[str, QueryObjectType]):
        self.bundle.queries = queries

    def type_check(self, obj: Any):
        is_subclass = inspect.isclass(obj) and issubclass(obj, QueryObjectType)
        return is_subclass and obj != QueryObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
