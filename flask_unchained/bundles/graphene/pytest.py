import graphql
import pytest

from flask_unchained import request, unchained
from graphene.test import Client as GrapheneClient


def _raise_non_graphql_exceptions(error):
    if isinstance(error, graphql.GraphQLError):
        return graphql.format_error(error)

    raise error


class GraphQLClient(GrapheneClient):
    def __init__(self, schema=None, format_error=None, **execute_options):
        super().__init__(schema or unchained.graphene_bundle.root_schema,
                         format_error=format_error or _raise_non_graphql_exceptions,
                         **execute_options)

    def execute(self, query, values=None):
        return super().execute(query, context_value=request, variable_values=values)


@pytest.fixture()
def graphql_client():
    yield GraphQLClient()
