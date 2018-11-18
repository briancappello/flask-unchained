import graphene

from flask_graphql import GraphQLView
from flask_unchained import Bundle, FlaskUnchained
from typing import *

from .object_types import MutationsObjectType, QueriesObjectType, SQLAlchemyObjectType


class GrapheneBundle(Bundle):
    name = 'graphene_bundle'

    root_schema: graphene.Schema = None
    """
    The root :class:`graphene.Schema` containing all discovered queries, mutations,
    and types. Automatically created.
    """

    mutations: Dict[str, Type[MutationsObjectType]] = {}
    queries: Dict[str, Type[QueriesObjectType]] = {}
    types: Dict[str, Type[SQLAlchemyObjectType]] = {}

    # FIXME add flask_unchained.bundles.controller.routes.view function and make
    # that the way of adding graphql routes
    def after_init_app(self, app: FlaskUnchained):
        if app.config.GRAPHENE_URL:
            app.add_url_rule(app.config.GRAPHENE_URL, view_func=GraphQLView.as_view(
                'graphql',
                schema=self.root_schema,
                graphiql=app.config.GRAPHENE_ENABLE_GRAPHIQL,
                pretty=app.config.GRAPHENE_PRETTY_JSON,
                batch=False,
            ))

        if app.config.GRAPHENE_BATCH_URL:
            app.add_url_rule(app.config.GRAPHENE_BATCH_URL, view_func=GraphQLView.as_view(
                'graphql',
                schema=self.root_schema,
                graphiql=app.config.GRAPHENE_ENABLE_GRAPHIQL,
                pretty=app.config.GRAPHENE_PRETTY_JSON,
                batch=True,
            ))


__all__ = [
    'GrapheneBundle',
    'MutationsObjectType',
    'QueriesObjectType',
    'SQLAlchemyObjectType',
]
