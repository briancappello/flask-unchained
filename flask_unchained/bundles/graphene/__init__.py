import graphene

from flask_graphql import GraphQLView
from flask_unchained import Bundle, FlaskUnchained
from typing import *

from .object_types import MutationObjectType, QueryObjectType, SQLAlchemyObjectType


class GrapheneBundle(Bundle):
    name = 'graphene_bundle'

    root_schema: graphene.Schema = None
    """
    The root :class:`graphene.Schema` containing all discovered queries, mutations,
    and types. Automatically created.
    """

    mutations: Dict[str, Type[MutationObjectType]] = {}
    queries: Dict[str, Type[QueryObjectType]] = {}
    types: Dict[str, Type[SQLAlchemyObjectType]] = {}

    # FIXME add flask_unchained.bundles.controller.routes.view function and make
    # that the way of adding graphql routes
    def after_init_app(self, app: FlaskUnchained):
        graphql_url = app.config.GRAPHENE_URL
        if graphql_url:
            app.add_url_rule(
                graphql_url,
                view_func=GraphQLView.as_view(
                    'graphql',
                    schema=self.root_schema,
                    graphiql=app.config.get('GRAPHENE_ENABLE_GRAPHIQL', False),
                    pretty=app.config.get('GRAPHENE_PRETTY_JSON', False),
                    batch=False,
                ))

        graphql_batch_url = app.config.GRAPHENE_BATCH_URL
        if graphql_batch_url:
            app.add_url_rule(
                graphql_batch_url,
                view_func=GraphQLView.as_view(
                    'graphql',
                    schema=self.root_schema,
                    graphiql=app.config.get('GRAPHENE_ENABLE_GRAPHIQL', False),
                    pretty=app.config.get('GRAPHENE_PRETTY_JSON', False),
                    batch=True,
                ))


__all__ = [
    'MutationObjectType',
    'QueryObjectType',
    'SQLAlchemyObjectType',
]
