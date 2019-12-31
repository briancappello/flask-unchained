import graphene

from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
from typing import *


class RegisterGrapheneRootSchemaHook(AppFactoryHook):
    name = 'graphene_root_schema'
    bundle_module_names = None
    run_after = ['graphene_queries', 'graphene_mutations']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        mutations = tuple(self.bundle.mutations.values())
        queries = tuple(self.bundle.queries.values())

        self.bundle.root_schema = graphene.Schema(
            query=queries and type('Queries', queries, {}) or None,
            mutation=mutations and type('Mutations', mutations, {}) or None,
            types=list(self.bundle.types.values()) or None)
