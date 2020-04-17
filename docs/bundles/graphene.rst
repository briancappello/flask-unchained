Graphene Bundle
---------------

Integrates `Flask GraphQL <https://github.com/graphql-python/flask-graphql>`_ and `Graphene-SQLAlchemy <http://docs.graphene-python.org/projects/sqlalchemy/en/latest/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

    pip install "flask-unchained[graphene]"

And enable the graphene bundle in your ``unchained_config.py``:

.. code:: python

    # project-root/unchained_config.py

    BUNDLES = [
        # ...
        'flask_unchained.bundles.graphene',
        'app',
    ]

Usage
^^^^^

Create a ``graphene`` module in your bundle:

.. code:: bash

    cd your_bundle
    mkdir graphene && touch graphene/__init__.py
    touch graphene/mutations.py graphene/queries.py graphene/types.py

Let's say you have some models you want to create a GraphQL schema for:

.. code-block::

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

Object Types
~~~~~~~~~~~~

The first step is to define your object types for your models:

.. code-block::

    # your_bundle/graphene/types.py

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

Queries
~~~~~~~

Next define the queries for your types:

.. code-block::

    # your_bundle/graphene/queries.py

    import graphene

    from flask_unchained.bundles.graphene import QueriesObjectType

    from . import types

    class Queries(QueriesObjectType):
        parent = graphene.Field(types.Parent, id=graphene.ID(required=True))
        parents = graphene.List(types.Parent)

        child = graphene.Field(types.Child, id=graphene.ID(required=True))
        children = graphene.List(types.Child)

When subclassing ``QueriesObjectType``, it automatically adds default resolvers for you. But these can be overridden if you want, eg:

.. code-block::

    # your_bundle/graphene/queries.py

    import graphene

    from flask_unchained import unchained
    from flask_unchained.bundles.graphene import QueriesObjectType

    from .. import services
    from . import types

    child_manager: services.ChildManager = unchained.get_local_proxy('child_manager')

    class Queries(QueriesObjectType):
        # ...
        children = graphene.List(types.Child, parent_id=graphene.ID())

        def resolve_children(self, info, parent_id=None, **kwargs):
            if not parent_id:
                return child_manager.all()
            return child_manager.filter_by_parent_id(parent_id).all()

.. admonition:: Note
    :class: warning

    Unfortunately, dependency injection does not work with graphene classes. (That said, you can still decorate individual methods with ``@unchained.inject()``.)

Mutations
~~~~~~~~~

Graphene mutations, per the :class:`~flask_unchained.bundles.graphene.RegisterGrapheneMutationsHook`, by default live in the ``graphene.mutations`` module of bundles. This can be customized by setting the ``graphene_mutations_module_names`` attribute on your bundle class.

.. code-block::

    import graphene

    from flask_unchained import unchained, injectable, lazy_gettext as _
    from flask_unchained.bundles.graphene import MutationsObjectType, MutationValidationError

    from flask_unchained.bundles.security.exceptions import AuthenticationError
    from flask_unchained.bundles.security.services import SecurityService, SecurityUtilsService
    from flask_unchained.bundles.security.graphene.types import UserInterface

    class LoginUser(graphene.Mutation):
        class Arguments:
            email = graphene.String(required=True)
            password = graphene.String(required=True)

        success = graphene.Boolean(required=True)
        message = graphene.String()
        user = graphene.Field(UserInterface)

        @unchained.inject('security_service')
        def mutate(
            self,
            info,
            email: str,
            password: str,
            security_service: SecurityService = injectable,
            **kwargs,
        ):
            try:
                user = LoginUser.validate(email, password)
            except MutationValidationError as e:
                return LoginUser(success=False, message=e.args[0])

            try:
                security_service.login_user(user)
            except AuthenticationError as e:
                return LoginUser(success=False, message=e.args[0])

            return LoginUser(success=True, user=user)

        @staticmethod
        @unchained.inject('security_utils_service')
        def validate(
            email: str,
            password: str,
            security_utils_service: SecurityUtilsService = injectable,
        ):
            user = security_utils_service.user_loader(email)
            if user is None:
                raise MutationValidationError(
                    _('flask_unchained.bundles.security:error.user_does_not_exist'))

            if not security_utils_service.verify_password(user, password):
                raise MutationValidationError(
                    _('flask_unchained.bundles.security:error.invalid_password'))

            return user

    class LogoutUser(graphene.Mutation):
        success = graphene.Boolean(required=True)

        @unchained.inject('security_service')
        def mutate(self, info, security_service: SecurityService = injectable, **kwargs):
            security_service.logout_user()
            return LogoutUser(success=True)

    class SecurityMutations(MutationsObjectType):
        login_user = mutations.LoginUser.Field(description="Login with email and password.")
        logout_user = mutations.LogoutUser.Field(description="Logout the current user.")

API Docs
^^^^^^^^

See :doc:`../api/graphene-bundle`
