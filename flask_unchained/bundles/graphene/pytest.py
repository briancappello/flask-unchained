import graphql
import pytest
import warnings

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
        # upstream claims the variable_values kwarg is deprecated by values,
        # except it only works using variable_values. so that's pretty sweet.
        with warnings.catch_warnings():
            filter_re = r'variable_values has been deprecated.[\w\s]+'
            warnings.filterwarnings('ignore', filter_re, DeprecationWarning)
            rv = super().execute(query, context=request, variable_values=values)

        # apparently it doesn't work to return from within the with block?
        return rv


@pytest.fixture()
def graphql_client():
    yield GraphQLClient()
