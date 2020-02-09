from flask_unchained import AppFactoryHook, FlaskUnchained
from typing import *

from ..object_types import QueriesObjectType


class RegisterGrapheneQueriesHook(AppFactoryHook):
    """
    Registers Graphene Queries with the Graphene Bundle.
    """

    name = 'graphene_queries'
    """
    The name of this hook.
    """

    bundle_module_names = ['graphene.queries', 'graphene.schema']
    """
    The default module this hook loads from.

    Override by setting the ``graphene_queries_module_names`` attribute on your
    bundle class.
    """

    bundle_override_module_names_attr = 'graphene_queries_module_names'
    run_after = ['graphene_types']

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def process_objects(self,
                        app: FlaskUnchained,
                        queries: Dict[str, QueriesObjectType]):
        """
        Register discovered queries with the Graphene Bundle.
        """
        self.bundle.queries = queries

    def type_check(self, obj: Any):
        """
        Returns True if ``obj`` is a subclass of
        :class:`~flask_unchained.bundles.graphene.QueriesObjectType`.
        """
        is_subclass = isinstance(obj, type) and issubclass(obj, QueriesObjectType)
        return is_subclass and obj != QueriesObjectType and (
                not hasattr(obj, 'Meta') or not getattr(obj.Meta, 'abstract', False))
