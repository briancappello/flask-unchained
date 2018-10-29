import graphene

from flask_unchained.bundles.graphene import SQLAlchemyObjectType

from .. import models


class Parent(SQLAlchemyObjectType):
    class Meta:
        model = models.Parent
        only_fields = ('id', 'name', 'created_at', 'updated_at')

    children = graphene.List(lambda: Child)


class Child(SQLAlchemyObjectType):
    class Meta:
        model = models.Child
        only_fields = ('id', 'name', 'created_at', 'updated_at')

    parent = graphene.Field(Parent)
