import graphene

from flask_unchained import unchained
from graphene.utils.subclass_with_meta import (
    SubclassWithMeta_Meta as _BaseObjectTypeMetaclass)
from graphene_sqlalchemy import SQLAlchemyObjectType as _SQLAObjectType
from graphene_sqlalchemy.types import (
    SQLAlchemyObjectTypeOptions as _SQLAObjectTypeOptions)


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


class _QueryObjectTypeMetaclass(_BaseObjectTypeMetaclass):
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


class QueryObjectType(graphene.ObjectType, metaclass=_QueryObjectTypeMetaclass):
    class Meta:
        abstract = True


class MutationObjectType(graphene.ObjectType):
    class Meta:
        abstract = True


# FIXME: probably should add a base class & hook for non-sqlalchemy types
