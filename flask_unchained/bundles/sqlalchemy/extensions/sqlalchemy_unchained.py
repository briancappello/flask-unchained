from flask_sqlalchemy_unchained import (
    SQLAlchemyUnchained as BaseSQLAlchemy,
    Query as BaseQuery,
)
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.sql.naming import (
    ConventionDict,
    _get_convention,
    conv as converted_name,
)
from sqlalchemy_unchained import (
    DeclarativeMeta,
    BaseValidator,
    Required,
    ValidationError,
    ValidationErrors,
)

from .. import sqla
from ..base_model import BaseModel
from ..services import SessionManager, ModelManager

from ..model_registry import UnchainedModelRegistry  # required import


class SQLAlchemyUnchained(BaseSQLAlchemy):
    """
    The `SQLAlchemyUnchained` extension::

        from flask_unchained.bundles.sqlalchemy import db

    Provides aliases for common SQLAlchemy stuffs:

    **sqlalchemy.schema**: Columns & Tables

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.schema.Column
        ~sqlalchemy.schema.Computed
        ~sqlalchemy.schema.ColumnDefault
        ~sqlalchemy.schema.DefaultClause
        ~sqlalchemy.schema.FetchedValue
        ~sqlalchemy.schema.ForeignKey
        ~sqlalchemy.schema.Index
        ~sqlalchemy.schema.Sequence
        ~sqlalchemy.schema.Table

    **sqlalchemy.schema**: Constraints

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.schema.CheckConstraint
        ~sqlalchemy.schema.Constraint
        ~sqlalchemy.schema.ForeignKeyConstraint
        ~sqlalchemy.schema.PrimaryKeyConstraint
        ~sqlalchemy.schema.UniqueConstraint

    **sqlalchemy.types**: Column types

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.types.BigInteger
        ~sqlalchemy.types.Boolean
        ~sqlalchemy.types.Date
        ~sqlalchemy.types.DateTime
        ~sqlalchemy.types.Enum
        ~sqlalchemy.types.Float
        ~sqlalchemy.types.Integer
        ~sqlalchemy.types.Interval
        ~sqlalchemy.types.LargeBinary
        ~sqlalchemy.types.Numeric
        ~sqlalchemy.types.PickleType
        ~sqlalchemy.types.SmallInteger
        ~sqlalchemy.types.String
        ~sqlalchemy.types.Text
        ~sqlalchemy.types.Time
        ~sqlalchemy.types.TypeDecorator
        ~sqlalchemy.types.Unicode
        ~sqlalchemy.types.UnicodeText

    **relationship helpers**

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.ext.associationproxy.association_proxy
        ~sqlalchemy.ext.declarative.declared_attr
        ~flask_unchained.bundles.sqlalchemy.sqla.foreign_key
        ~sqlalchemy.ext.hybrid.hybrid_method
        ~sqlalchemy.ext.hybrid.hybrid_property
        ~sqlalchemy.orm.relationship

    **sqlalchemy.types**: SQL types

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.types.ARRAY
        ~sqlalchemy.types.BIGINT
        ~sqlalchemy.types.BINARY
        ~sqlalchemy.types.BLOB
        ~sqlalchemy.types.BOOLEAN
        ~sqlalchemy.types.CHAR
        ~sqlalchemy.types.CLOB
        ~sqlalchemy.types.DATE
        ~sqlalchemy.types.DATETIME
        ~sqlalchemy.types.DECIMAL
        ~sqlalchemy.types.FLOAT
        ~sqlalchemy.types.INT
        ~sqlalchemy.types.INTEGER
        ~sqlalchemy.types.JSON
        ~sqlalchemy.types.NCHAR
        ~sqlalchemy.types.NUMERIC
        ~sqlalchemy.types.NVARCHAR
        ~sqlalchemy.types.REAL
        ~sqlalchemy.types.SMALLINT
        ~sqlalchemy.types.TEXT
        ~sqlalchemy.types.TIME
        ~sqlalchemy.types.TIMESTAMP
        ~sqlalchemy.types.VARBINARY
        ~sqlalchemy.types.VARCHAR

    **sqlalchemy.schema**

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.schema.DDL
        ~sqlalchemy.schema.MetaData
        ~sqlalchemy.schema.ThreadLocalMetaData

    **sqlalchemy.sql.expression**

    .. autosummary::
        :nosignatures:

        ~sqlalchemy.sql.expression.alias
        ~sqlalchemy.sql.expression.all_
        ~sqlalchemy.sql.expression.and_
        ~sqlalchemy.sql.expression.any_
        ~sqlalchemy.sql.expression.asc
        ~sqlalchemy.sql.expression.between
        ~sqlalchemy.sql.expression.bindparam
        ~sqlalchemy.sql.expression.case
        ~sqlalchemy.sql.expression.cast
        ~sqlalchemy.sql.expression.collate
        ~sqlalchemy.sql.expression.column
        ~sqlalchemy.sql.expression.delete
        ~sqlalchemy.sql.expression.desc
        ~sqlalchemy.sql.expression.distinct
        ~sqlalchemy.sql.expression.except_
        ~sqlalchemy.sql.expression.except_all
        ~sqlalchemy.sql.expression.exists
        ~sqlalchemy.sql.expression.extract
        ~sqlalchemy.sql.expression.false
        ~sqlalchemy.sql.expression.func
        ~sqlalchemy.sql.expression.funcfilter
        ~sqlalchemy.sql.expression.insert
        ~sqlalchemy.sql.expression.intersect
        ~sqlalchemy.sql.expression.intersect_all
        ~sqlalchemy.sql.expression.join
        ~sqlalchemy.sql.expression.lateral
        ~sqlalchemy.sql.expression.literal
        ~sqlalchemy.sql.expression.literal_column
        ~sqlalchemy.sql.expression.not_
        ~sqlalchemy.sql.expression.null
        ~sqlalchemy.sql.expression.nullsfirst
        ~sqlalchemy.sql.expression.nullslast
        ~sqlalchemy.sql.expression.or_
        ~sqlalchemy.sql.expression.outerjoin
        ~sqlalchemy.sql.expression.outparam
        ~sqlalchemy.sql.expression.over
        ~sqlalchemy.sql.expression.select
        ~sqlalchemy.sql.expression.subquery
        ~sqlalchemy.sql.expression.table
        ~sqlalchemy.sql.expression.tablesample
        ~sqlalchemy.sql.expression.text
        ~sqlalchemy.sql.expression.true
        ~sqlalchemy.sql.expression.tuple_
        ~sqlalchemy.sql.expression.type_coerce
        ~sqlalchemy.sql.expression.union
        ~sqlalchemy.sql.expression.union_all
        ~sqlalchemy.sql.expression.update
        ~sqlalchemy.sql.expression.within_group
    """

    def __init__(
        self,
        app=None,
        *,
        metadata=None,
        session_options=None,
        query_class=BaseQuery,
        model_class=BaseModel,
        engine_options=None,
    ):
        super().__init__(
            app,
            metadata=metadata,
            session_options=session_options,
            query_class=query_class,
            model_class=model_class,
            engine_options=engine_options,
            add_models_to_shell=False,
        )
        SessionManager.set_session_factory(lambda: self.session())

        self.ModelManager = ModelManager

        self.Column = sqla.Column
        self.BigInteger = sqla.BigInteger
        self.DateTime = sqla.DateTime
        self.foreign_key = sqla.foreign_key

        self.BaseValidator = BaseValidator
        self.Required = Required
        self.ValidationError = ValidationError
        self.ValidationErrors = ValidationErrors

        self.attach_events = sqla.attach_events
        self.on = sqla.on
        self.slugify = sqla.slugify

        # a bit of hackery to make type-hinting in PyCharm work better
        if False:
            self.Column = sqla._column_type_hinter_
            self.backref = sqla._relationship_type_hinter_
            self.relationship = sqla._relationship_type_hinter_
            self.session = Session

    def init_app(self, app):
        self.app = app
        super().init_app(app)

    def _set_constraint_name(self, const, table):
        fmt = _get_convention(self.metadata.naming_convention, type(const))
        if not fmt:
            return

        const.name = converted_name(
            fmt % ConventionDict(const, table, self.metadata.naming_convention)
        )
