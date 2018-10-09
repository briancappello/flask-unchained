from flask_sqlalchemy_unchained import BaseModel as _BaseModel, BaseQuery
from ...bundles.babel import lazy_gettext as _
from ...string_utils import pluralize, title_case
from sqlalchemy.ext.declarative import declared_attr
from typing import *

from .meta_options import ModelMetaOptionsFactory


class QueryAliasDescriptor:
    def __get__(self, instance, cls):
        return cls.query


class BaseModel(_BaseModel):
    """
    Base model class
    """
    _meta_options_factory_class = ModelMetaOptionsFactory
    gettext_fn = _

    query: BaseQuery
    q: BaseQuery = QueryAliasDescriptor()

    @declared_attr
    def __plural__(self):
        return pluralize(self.__name__)

    @declared_attr
    def __label__(self):
        return title_case(self.__name__)

    @declared_attr
    def __plural_label__(self):
        return title_case(pluralize(self.__name__))


class QueryableBaseModel(BaseModel):
    def all(self) -> List[BaseModel]:
        return self.q.all()

    def get(self, id) -> Union[None, BaseModel]:
        """
        Return an instance based on the given primary key identifier,
        or ``None`` if not found.

        For example::

            my_user = session.query(User).get(5)

            some_object = session.query(VersionedFoo).get((5, 10))

        :meth:`~.Query.get` is special in that it provides direct
        access to the identity map of the owning :class:`.Session`.
        If the given primary key identifier is present
        in the local identity map, the object is returned
        directly from this collection and no SQL is emitted,
        unless the object has been marked fully expired.
        If not present,
        a SELECT is performed in order to locate the object.

        :meth:`~.Query.get` also will perform a check if
        the object is present in the identity map and
        marked as expired - a SELECT
        is emitted to refresh the object as well as to
        ensure that the row is still present.
        If not, :class:`~sqlalchemy.orm.exc.ObjectDeletedError` is raised.

        :meth:`~.Query.get` is only used to return a single
        mapped instance, not multiple instances or
        individual column constructs, and strictly
        on a single primary key value.  The originating
        :class:`.Query` must be constructed in this way,
        i.e. against a single mapped entity,
        with no additional filtering criterion.  Loading
        options via :meth:`~.Query.options` may be applied
        however, and will be used if the object is not
        yet locally present.

        A lazy-loading, many-to-one attribute configured
        by :func:`.relationship`, using a simple
        foreign-key-to-primary-key criterion, will also use an
        operation equivalent to :meth:`~.Query.get` in order to retrieve
        the target value from the local identity map
        before querying the database.  See :doc:`/orm/loading_relationships`
        for further details on relationship loading.

        :param id: A scalar or tuple value representing
         the primary key.   For a composite primary key,
         the order of identifiers corresponds in most cases
         to that of the mapped :class:`.Table` object's
         primary key columns.  For a :func:`.mapper` that
         was given the ``primary key`` argument during
         construction, the order of identifiers corresponds
         to the elements present in this collection.

        :return: The model instance, or ``None``.
        """
        return self.q.get(id)

    def get_by(self, **kwargs) -> Union[None, BaseModel]:
        return self.q.get_by(**kwargs)

    def filter_by(self, **kwargs) -> List[BaseModel]:
        return self.q.filter_by(**kwargs).all()
