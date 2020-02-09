import graphene

from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from typing import *


class RegisterGrapheneRootSchemaHook(AppFactoryHook):
    """
    Creates the root :class:`graphene.Schema` to register with Flask-GraphQL.
    """

    name = 'graphene_root_schema'
    """
    The name of this hook.
    """

    bundle_module_names = None
    run_after = ['graphene_queries', 'graphene_mutations']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        """
        Create the root :class:`graphene.Schema` from queries, mutations, and types
        discovered by the other hooks and register it with the Graphene Bundle.
        """
        mutations = tuple(self.bundle.mutations.values())
        queries = tuple(self.bundle.queries.values())
        types = list(self.bundle.types.values())

        self.bundle.root_schema = graphene.Schema(
            query=queries and type('Queries', queries, {}) or None,
            mutation=mutations and type('Mutations', mutations, {}) or None,
            types=types or None)
