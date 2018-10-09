from flask_unchained import unchained
from flask_unchained.di import ServiceMetaOptionsFactory
from flask_sqlalchemy_unchained import BaseQuery
from typing import *

from ..base_model import BaseModel as Model
from ..meta_options import ModelMetaOption
from .session_manager import SessionManager


class ModelManagerMetaOptionsFactory(ServiceMetaOptionsFactory):
    options = ServiceMetaOptionsFactory.options + [ModelMetaOption]


class ModelManager(SessionManager):
    """
    Base class for model managers.
    """
    _meta_options_factory_class = ModelManagerMetaOptionsFactory

    class Meta:
        abstract = True
        model = None

    def __init__(self):
        super().__init__()
        try:
            self.Meta.model = unchained.sqlalchemy_bundle.models[self.Meta.model.__name__]
        except (AttributeError, KeyError):
            pass

    @property
    def q(self) -> BaseQuery:
        """
        Alias for :meth:`query`.
        """
        return self.Meta.model.query

    @property
    def query(self) -> BaseQuery:
        """
        Returns the query class for this manager's model
        """
        return self.Meta.model.query

    def create(self, commit=False, **kwargs) -> Model:
        """
        Creates an instance of the model, adding it to the database session,
        and optionally commits the session.

        :param commit: Whether or not to commit the database session.
        :param kwargs: The data to initialize the model with.
        :return: The model instance.
        """
        instance = self.Meta.model(**kwargs)
        self.save(instance, commit=commit)
        return instance

    def update(self, instance, commit=False, **kwargs) -> Model:
        """
        Updates a model instance, adding it to the database session,
        and optionally commits the session.

        :param instance: The model instance to update.
        :param commit: Whether or not to commit the database session.
        :param kwargs: The data to update on the model.
        :return: The model instance.
        """
        instance.update(**kwargs)
        self.save(instance, commit=commit)
        return instance

    def all(self) -> List[Model]:
        return self.q.all()

    def get(self, id) -> Union[None, Model]:
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

    def get_or_create(self, commit=False, **kwargs) -> Tuple[Model, bool]:
        """
        :return: returns a tuple of the instance and a boolean flag specifying
                 whether or not the instance was created
        """
        instance = self.get_by(**kwargs)
        if not instance:
            return self.create(commit=commit, **kwargs), True
        return instance, False

    def get_by(self, **kwargs) -> Union[None, Model]:
        return self.q.get_by(**kwargs)

    def filter_by(self, **kwargs) -> List[Model]:
        return self.q.filter_by(**kwargs).all()
