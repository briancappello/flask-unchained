import graphene

from flask_unchained import unchained
from flask_unchained.bundles.sqlalchemy import SessionManager, ValidationErrors
from graphql import GraphQLError

from . import types


session_manager: SessionManager = unchained.get_local_proxy('session_manager')


class CreateParent(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        children = graphene.List(graphene.ID)

    parent = graphene.Field(types.Parent)
    success = graphene.Boolean()

    def mutate(self, info, children, **kwargs):
        if children:
            children = (session_manager
                            .query(types.Child._meta.model)
                            .filter(types.Child._meta.model.id.in_(children))
                            .all())
        try:
            parent = types.Parent._meta.model(children=children, **kwargs)
        except ValidationErrors as e:
            raise GraphQLError(str(e))

        session_manager.save(parent, commit=True)
        return CreateParent(parent=parent, success=True)


class DeleteParent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    id = graphene.Int()
    success = graphene.Boolean()

    def mutate(self, info, id):
        parent = session_manager.query(types.Parent._meta.model).get(id)
        session_manager.delete(parent, commit=True)
        return DeleteParent(id=id, success=True)


class EditParent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        children = graphene.List(graphene.ID)

    parent = graphene.Field(types.Parent)
    success = graphene.Boolean()

    def mutate(self, info, id, children, **kwargs):
        parent = session_manager.query(types.Parent._meta.model).get(id)

        try:
            parent.update(**{k: v for k, v in kwargs.items() if v})
        except ValidationErrors as e:
            raise GraphQLError(str(e))

        if children:
            parent.children = (session_manager
                                   .query(types.Child._meta.model)
                                   .filter(types.Child._meta.model.id.in_(children))
                                   .all())

        session_manager.save(parent, commit=True)
        return EditParent(parent=parent, success=True)
