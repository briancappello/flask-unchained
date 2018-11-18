import graphene

from flask_unchained.bundles.graphene import MutationsObjectType, QueriesObjectType

from . import types
from . import mutations


class GrapheneBundleQueries(QueriesObjectType):
    parent = graphene.Field(types.Parent, id=graphene.ID(required=True))
    parents = graphene.List(types.Parent)

    child = graphene.Field(types.Child, id=graphene.ID(required=True))
    children = graphene.List(types.Child)


class GrapheneBundleMutations(MutationsObjectType):
    create_parent = mutations.CreateParent.Field()
    delete_parent = mutations.DeleteParent.Field()
    edit_parent = mutations.EditParent.Field()
