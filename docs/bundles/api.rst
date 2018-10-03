API Bundle
----------

Integrates `Marshmallow <https://marshmallow.readthedocs.io/en/2.x-line/>`_ and `APISpec <http://apispec.readthedocs.io/en/stable/>`_ with `SQLAlchemy <https://www.sqlalchemy.org/>`_ and `Flask Unchained <https://flask-unchained.readthedocs.io/en/latest/>`_.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install flask-unchained[api]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.api',
       'app',
   ]

Usage
^^^^^

The API bundle includes two extensions, :class:`~flask_unchained.bundles.api.Api` and :class:`~flask_unchained.bundles.api.Marshmallow`. :class:`~flask_unchained.bundles.api.Api` is used for generating OpenAPI documentation while :class:`~flask_unchained.bundles.api.Marshmallow` is used for serialization. These should be imported like so:

.. code:: python

   from flask_unchained.bundles.api import api, ma

Model Serializers
~~~~~~~~~~~~~~~~~

:class:`~flask_unchained.bundles.api.ModelSerializer` is very similar to Flask Marshmallow's :class:`~flask_marshmallow.sqla.ModelSchema`. There are two differences:

- dependency injection is automatically set up on the constructor, and
- we automatically convert field names to camel case when dumping and loading

Let's say you have the following model:

.. code:: python

   # your_bundle/models.py

   from flask_unchained.bundles.sqlalchemy import db

   class User(db.Model):
       name = db.Column(db.String)
       email = db.Column(db.String)
       password = db.Column(db.String)

A simple serializer for it would look like this:

.. code:: python

   # your_bundle/serializers.py

   from flask_unchained.bundles.api import ma

   from .models import User


   class UserSerializer(ma.ModelSerializer):
       class Meta:
           model = User

One gotchya here is that Marshmallow has no way to know that the email column should use an email field. Therefore, we need to help it out a bit:

.. code:: python

   # your_bundle/serializers.py

   from flask_unchained.bundles.api import ma

   from .models import User


   class UserSerializer(ma.ModelSerializer):
       class Meta:
           model = User
           load_only = ('password',)

       email = ma.Email(required=True)

There are three separate contexts for (de)serialization:

- standard: dumping/loading a single object
- many: dumping/loading multiple objects
- create: creating a new object

By default, any serializers you define will be used for all three. This can be customized:

.. code:: python

   # your_bundle/serializers.py

   from flask_unchained.bundles.api import ma

   @ma.serializer(many=True)
   class UserSerializerMany(ma.ModelSerializer):
       # ...

   @ma.serializer(create=True)
   class UserSerializerCreate(ma.ModelSerializer):
       # ...

Let's make a model resource so we'll have API routes for it:

Model Resources
~~~~~~~~~~~~~~~

.. code:: python

   # your_bundle/views.py

   from flask_unchained.bundles.api import ModelResource

   from .models import User


   class UserResource(ModelResource):
       class Meta:
           model = User

Add it to your routes:

.. code:: python

   # your_app_bundle/routes.py

   routes = lambda: [
       prefix('/api/v1', [
           resource('/users', UserResource),
       ],
   ]

And that's it, unless you need to customize any behavior.

Model Resource Meta Options
"""""""""""""""""""""""""""

:class:`~flask_unchained.bundles.api.ModelResource` inherits all of the meta options from :class:`~flask_unchained.Controller` and :class:`~flask_unchained.Resource`, and it adds some options of its own:

.. list-table::
   :header-rows: 1

   * - meta option name
     - description
     - default value
   * - model
     - The model class to use for the resource.
     - ``None`` (it's required to be set by you)
   * - serializer
     - The serializer instance to use for (de)serializing an individual model.
     - Determined automatically by the model name. Can be set manually to override the automatic discovery.
   * - serializer_create
     - The serializer instance to use for loading data for creation of a new model.
     - Determined automatically by the model name. Can be set manually to override the automatic discovery.
   * - serializer_many
     - The serializer instance to use for (de)serializing a list of models.
     - Determined automatically by the model name. Can be set manually to override the automatic discovery.
   * - include_methods
     - A list of resource methods to automatically include.
     - ``('list', 'create', 'get', 'patch', 'put', 'delete')``
   * - exclude_methods
     - A list of resource methods to exclude.
     - ``()``
   * - include_decorators
     - A list of resource methods for which to automatically apply the default decorators.
     - ``('list', 'create', 'get', 'patch', 'put', 'delete')``
   * - exclude_decorators
     - A list of resource methods for which to *not* automatically apply the default decorators.
     - ``()``
   * - method_decorators
     - This can either be a list of decorators to apply to *all* methods, or a dictionary of method names to a list of decorators to apply for each method. In both cases, decorators specified here are run *before* the default decorators.
     - ``()``

FIXME: OpenAPI Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/api`
