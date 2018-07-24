from flask_sqlalchemy import DefaultMeta, SQLAlchemy as BaseSQLAlchemy
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql.naming import (ConventionDict, _get_convention,
                                   conv as converted_name)

from .. import sqla
from ..base_model import BaseModel
from ..base_query import BaseQuery
from ..meta.base_model_metaclass import BaseModelMetaclass
from ..meta.model_registry import _model_registry
from ..validation import (
    BaseValidator, Required, ValidationError, ValidationErrors, validates)


class SQLAlchemy(BaseSQLAlchemy):
    def __init__(self, app=None, use_native_unicode=True, session_options=None,
                 metadata=None, query_class=BaseQuery, model_class=BaseModel):
        super().__init__(app, use_native_unicode=use_native_unicode,
                         session_options=session_options,
                         metadata=metadata,
                         query_class=query_class,
                         model_class=model_class)

        _model_registry.register_base_model_class(self.Model)

        self.Column = sqla.Column
        self.BigInteger = sqla.BigInteger
        self.DateTime = sqla.DateTime

        self.association_proxy = sqla.association_proxy
        self.declared_attr = sqla.declared_attr
        self.foreign_key = sqla.foreign_key
        self.hybrid_method = sqla.hybrid_method
        self.hybrid_property = sqla.hybrid_property

        self.validates = validates
        self.BaseValidator = BaseValidator
        self.Required = Required
        self.ValidationError = ValidationError
        self.ValidationErrors = ValidationErrors

        self.attach_events = sqla.attach_events
        self.on = sqla.on
        self.slugify = sqla.slugify

        self.refresh_materialized_view = sqla.refresh_materialized_view
        self.refresh_all_materialized_views = sqla.refresh_all_materialized_views

        class MaterializedViewMetaclass(BaseModelMetaclass):
            def _pre_mcs_init(cls):
                cls.__table__ = sqla.create_materialized_view(cls._meta.table,
                                                              cls.selectable())

            def _post_mcs_init(cls):
                # create a unique index for the primary key(s) of __table__
                cls._meta._refresh_concurrently = False
                for pk in cls.__table__.primary_key.columns:
                    pk_idx = self.Index(pk.name,
                                        getattr(cls, pk.name),
                                        unique=True)
                    self._set_constraint_name(pk_idx, cls.__table__)
                    cls._meta._refresh_concurrently = True

                # apply naming conventions to user-supplied indexes (if any)
                constraints = cls.constraints()
                for idx in constraints:
                    self._set_constraint_name(idx, cls.__table__)

                # automatically refresh the view when its parent table changes
                mv_for = cls._meta.mv_for
                parents = (mv_for if isinstance(mv_for, (list, tuple))
                           else [mv_for])
                for Parent in parents:
                    if isinstance(Parent, str):
                        Parent = cls._decl_class_registry[Parent]

                    def refresh_mv(mapper, connection, target):
                        cls.refresh()

                    event.listen(Parent, 'after_insert', refresh_mv)
                    event.listen(Parent, 'after_update', refresh_mv)
                    event.listen(Parent, 'after_delete', refresh_mv)

        class MaterializedView(self.Model, metaclass=MaterializedViewMetaclass):
            class Meta:
                abstract = True
                pk = None
                created_at = None
                updated_at = None

            @sqla.declared_attr
            def __tablename__(self):
                return self.__table__.fullname

            @classmethod
            def selectable(cls):
                """
                Return the selectable representing the materialized view. A
                unique index will automatically be created on its primary key.
                """
                raise NotImplementedError

            @classmethod
            def constraints(cls):
                return []

            @classmethod
            def refresh(cls, concurrently=None):
                concurrently = (concurrently if concurrently is not None
                                else cls._meta._refresh_concurrently)
                sqla.refresh_materialized_view(cls.__tablename__, concurrently)

        self.MaterializedView = MaterializedView

        # a bit of hackery to make type-hinting in PyCharm work better
        if False:
            self.Column = sqla._column_type_hinter_
            self.backref = sqla._relationship_type_hinter_
            self.relationship = sqla._relationship_type_hinter_
            self.session = Session

    def _set_constraint_name(self, const, table):
        fmt = _get_convention(self.metadata.naming_convention, type(const))
        if not fmt:
            return

        const.name = converted_name(
            fmt % ConventionDict(const, table, self.metadata.naming_convention))

    def make_declarative_base(self, model, metadata=None) -> BaseModel:
        if not isinstance(model, DefaultMeta):
            def make_model_class(name, bases, clsdict):
                clsdict['__abstract__'] = True
                clsdict['__module__'] = model.__module__
                if hasattr(model, 'Meta'):
                    clsdict['Meta'] = model.Meta
                if hasattr(model, '_meta_factory_class'):
                    clsdict['_meta_factory_class'] = model._meta_factory_class
                return BaseModelMetaclass(name, bases, clsdict)

            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=make_model_class,
                constructor=None,  # use the constructor declared on the base class
            )
        return super().make_declarative_base(model, metadata)
