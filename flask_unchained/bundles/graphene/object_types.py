import graphene

from flask_unchained import unchained
from flask_unchained.bundles.sqlalchemy.sqla.types import BigInteger
from graphene.utils.subclass_with_meta import (
    SubclassWithMeta_Meta as _BaseObjectTypeMetaclass)
from graphene_sqlalchemy import SQLAlchemyObjectType as _SQLAObjectType
from graphene_sqlalchemy.converter import (
    convert_sqlalchemy_type, convert_column_to_int_or_id, get_column_doc, is_column_nullable)
from graphene_sqlalchemy.types import (
    SQLAlchemyObjectTypeOptions as _SQLAObjectTypeOptions)
from sqlalchemy import types
from sqlalchemy.orm import class_mapper


# convert_sqlalchemy_type.register(BigInteger)(convert_column_to_int_or_id)
# convert_sqlalchemy_type.register(types.BigInteger)(convert_column_to_int_or_id)

@convert_sqlalchemy_type.register(BigInteger)
@convert_sqlalchemy_type.register(types.BigInteger)
def convert_column_to_int_or_id(type, column, registry=None):
    if column.primary_key or column.foreign_keys:
        return graphene.ID(
            description=get_column_doc(column),
            required=not (is_column_nullable(column)),
        )
    else:
        return graphene.Int(
            description=get_column_doc(column),
            required=not (is_column_nullable(column)),
        )


class SQLAlchemyObjectTypeOptions(_SQLAObjectTypeOptions):
    """
    This class stores the meta options for :class:`SQLAlchemyObjectType`.

    Overridden only to add compatibility with the SQLAlchemy bundle; otherwise
    supports the same options as
    :class:`graphene_sqlalchemy.types.SQLAlchemyObjectTypeOptions`.
    """
    def __init__(self, class_type):
        super().__init__(class_type)
        self._model = None

    @property
    def model(self):
        # make sure to always return the correct mapped model class
        if not unchained._models_initialized or not self._model:
            return self._model
        return unchained.sqlalchemy_bundle.models[self._model.__name__]

    @model.setter
    def model(self, model):
        self._model = model


class SQLAlchemyObjectType(_SQLAObjectType):
    """
    Base class for SQLAlchemy model object types. Acts exactly the same as
    :class:`graphene_sqlalchemy.SQLAlchemyObjectType`, except we've added
    compatibility with the SQLAlchemy Bundle.

    Example usage::

        # your_bundle/models.py

        from flask_unchained.bundles.sqlalchemy import db

        class Parent(db.Model):
            name = db.Column(db.String)

            children = db.relationship('Child', back_populates='parent',
                                       cascade='all,delete,delete-orphan')

        class Child(db.Model):
            name = db.Column(db.String)

            parent_id = db.foreign_key('Parent')
            parent = db.relationship('Parent', back_populates='children')


        # your_bundle/graphql/types.py

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
    """
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, model=None, registry=None,
                                    skip_registry=False,
                                    only_fields=(), exclude_fields=(),
                                    connection=None, connection_class=None,
                                    use_connection=None, interfaces=(),
                                    id=None, _meta=None, **options):
        if _meta and not isinstance(_meta, SQLAlchemyObjectTypeOptions):
            raise TypeError(f'Your _meta ObjectTypeOptions class must extend '
                            f'{SQLAlchemyObjectTypeOptions.__qualname__}')

        # make sure we provide graphene the correct mapped model class
        if unchained._models_initialized:
            model = unchained.sqlalchemy_bundle.models[model.__name__]

            # graphene has a horrible habit of eating exceptions and this is one
            # place where it does, so we preempt it (if this fails it should throw)
            class_mapper(model)

        return super().__init_subclass_with_meta__(
            model=model, registry=registry, skip_registry=skip_registry,
            only_fields=only_fields, exclude_fields=exclude_fields,
            connection=connection, connection_class=connection_class,
            use_connection=use_connection, interfaces=interfaces,
            id=id, _meta=_meta or SQLAlchemyObjectTypeOptions(cls), **options)


def _get_field_resolver(field: graphene.Field):
    def _get(self, info, **kwargs):
        return field.type._meta.model.query.get_by(**kwargs)

    return _get


def _get_list_resolver(list_: graphene.List):
    def _get_list(self, info, **kwargs):
        return list_.of_type._meta.model.query.all()

    return _get_list


class _QueriesObjectTypeMetaclass(_BaseObjectTypeMetaclass):
    def __new__(mcs, name, bases, clsdict):
        fields, lists = [], []
        for attr, value in clsdict.items():
            resolver = f'resolve_{attr}'
            if attr.startswith('_') or resolver in clsdict:
                continue
            elif isinstance(value, graphene.Field):
                fields.append((resolver, value))
            elif isinstance(value, graphene.List):
                lists.append((resolver, value))

        clsdict.update({k: _get_field_resolver(v) for k, v in fields})
        clsdict.update({k: _get_list_resolver(v) for k, v in lists})

        return super().__new__(mcs, name, bases, clsdict)


class QueriesObjectType(graphene.ObjectType, metaclass=_QueriesObjectTypeMetaclass):
    """
    Base class for ``query`` schema definitions. :class:`graphene.Field` and
    :class:`graphene.List` fields are automatically resolved (but you can
    write your own and it will disable the automatic behavior for that field).

    Example usage::

        # your_bundle/graphql/schema.py

        from flask_unchained.bundles.graphene import QueriesObjectType

        from . import types

        class YourBundleQueries(QueriesObjectType):
            parent = graphene.Field(types.Parent, id=graphene.ID(required=True))
            parents = graphene.List(types.Parent)

            child = graphene.Field(types.Child, id=graphene.ID(required=True))
            children = graphene.List(types.Child)

            # this is what the default resolvers do, and how you would override them:
            def resolve_child(self, info, **kwargs):
                return types.Child._meta.model.query.get_by(**kwargs)

            def resolve_children(self, info, **kwargs):
                return types.Child._meta.model.query.all()
    """
    class Meta:
        abstract = True


class MutationsObjectType(graphene.ObjectType):
    """
    Base class for ``mutation`` schema definitions.

    Example usage::

        #  your_bundle/graphql/mutations.py

        import graphene

        from flask_unchained import unchained
        from flask_unchained.bundles.sqlalchemy import SessionManager, db
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
                except db.ValidationErrors as e:
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
                except db.ValidationErrors as e:
                    raise GraphQLError(str(e))

                if children:
                    parent.children = (session_manager
                                           .query(types.Child._meta.model)
                                           .filter(types.Child._meta.model.id.in_(children))
                                           .all())

                session_manager.save(parent, commit=True)
                return EditParent(parent=parent, success=True)


        # your_bundle/graphql/schema.py

        from flask_unchained.bundles.graphene import MutationsObjectType

        from . import mutations

        class YourBundleMutations(MutationsObjectType):
            create_parent = mutations.CreateParent.Field()
            delete_parent = mutations.DeleteParent.Field()
            edit_parent = mutations.EditParent.Field()
    """
    class Meta:
        abstract = True


# FIXME: probably should add a base class & hook for non-sqlalchemy types
