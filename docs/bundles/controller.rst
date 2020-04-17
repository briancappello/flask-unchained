Controller Bundle
-----------------

The controller bundle provides the primary means for defining views and registering their routes with Flask. It is also the controller bundle that makes all of your other bundles blueprints.

Installation
^^^^^^^^^^^^

The controller bundle comes enabled by default.

Usage
^^^^^

Config
~~~~~~

.. automodule:: flask_unchained.bundles.controller.config
   :members:
   :noindex:

Views and Controllers
~~~~~~~~~~~~~~~~~~~~~

Like stock Flask, Flask Unchained supports using views defined the "standard" way, ie::

   # your_app/views.py

   from flask import Blueprint, render_template


   bp = Blueprint('bp', __name__)

   @bp.route('/foo')
   def foo():
      return render_template('bp/foo.html')

View functions defined this way have a major drawback, however. And that is, as soon as this code gets imported, the view's route gets registered with the app. Most of the time this is the desired behavior, and it will work as expected with code placed in your app bundle, however bundles meant for distribution to third parties must avoid defining views in this way, because it makes it impossible for the view to be overridden and/or its route to be customized.

The recommended way to define views with Flask Unchained is by using controller classes::

   # your_app_bundle/views.py

   from flask_unchained import Controller, route


   class SiteController(Controller):
      @route('/foo')
      def foo():
         return self.render('foo')

This view will do the same thing as the prior example view, however, using :class:`~flask_unchained.Controller` as the base class has the advantage of making views and their routes easily and independently customizable. Controllers also support automatic dependency injection and include some convenience methods such as :meth:`~flask_unchained.Controller.flash`, :meth:`~flask_unchained.Controller.jsonify`, :meth:`~flask_unchained.Controller.redirect`, and :meth:`~flask_unchained.Controller.render`.

Unlike when using the stock Flask decorators to register a view's routes, in Flask Unchained we must explicitly enable the routes we want::

   # your_app_bundle/routes.py

   from flask_unchained import (controller, resource, func, include, prefix,
                                get, delete, post, patch, put, rule)

   from .views import SiteController


   routes = lambda: [
       controller(SiteController),
   ]

By default this code will register all of the view functions on ``SiteController`` with the app, using the default routing rules as defined on the view methods of the controller.

Declarative Routing
~~~~~~~~~~~~~~~~~~~

Declaration of routes in Flask Unchained can be uncoupled from the definition of the views themselves. Using function- and class-based views is supported. You already saw a simple example above, that would register a single route at ``/foo`` for the ``SiteController.foo`` method. Let's say we wanted to change it to ``/site/foobar``::

   # your_app_bundle/routes.py

   from flask_unchained import (controller, resource, func, include, prefix,
                                get, delete, post, patch, put, rule)

   from .views import SiteController

   routes = lambda: [
       # this is probably the clearest way to do it:
       controller('/site', SiteController, rules=[
           get('/foobar', SiteController.foo),
       ]),

       # or you can provide the method name of the controller as a string:
       controller('/site', SiteController, rules=[
           get('/foobar', 'foo'),
       ]),

       # or use nesting to produce the same result (this is especially useful when
       # you want to prefix more than one view/route with the same url prefix)
       prefix('/site', [
           controller(SiteController, rules=[
               get('/foobar', SiteController.foo),
           ]),
       ]),
   ]

Here is a summary of the functions imported at the top of your ``routes.py``:

.. list-table:: Declarative Routing Functions
   :header-rows: 1
   :widths: 20 80

   * - Function
     - Description
   * - :func:`~flask_unchained.include`
     - Include all of the routes from the specified module at that point in the tree.
   * - :func:`~flask_unchained.prefix`
     - Prefixes all of the child routing rules with the given prefix.
   * - :func:`~flask_unchained.func`
     - Registers a function-based view with the app, optionally specifying the routing rules.
   * - :func:`~flask_unchained.controller`
     - Registers a controller and its views with the app, optionally customizing the routes to register.
   * - :func:`~flask_unchained.resource`
     - Registers a resource and its views with the app, optionally customizing the routes to register.
   * - :func:`~flask_unchained.rule`
     - Define customizations to a controller/resource method's route rules.
   * - :func:`~flask_unchained.get`
     - Defines a controller/resource method as only accepting the HTTP ``GET`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.patch`
     - Defines a controller/resource method as only accepting the HTTP ``PATCH`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.post`
     - Defines a controller/resource method as only accepting the HTTP ``POST`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.put`
     - Defines a controller/resource method as only accepting the HTTP ``PUT`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.delete`
     - Defines a controller/resource method as only accepting the HTTP ``DELETE`` method, otherwise the same as :func:`~flask_unchained.rule`.

Class-Based Views
~~~~~~~~~~~~~~~~~

The controller bundle includes two base classes that all of your views should extend. The first is :class:`~flask_unchained.Controller`, which is implemented very similarly to :class:`~flask.views.View`, however they're not compatible. The second is :class:`~flask_unchained.Resource`, which extends :class:`~flask_unchained.Controller`, and whose implementation draws a lot of inspiration from `Flask-RSETful <https://flask-restful.readthedocs.io/en/latest/>`_ (specifically, the `Resource <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L543>`_ and `Api <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L38>`_ classes).

Controller
""""""""""

Unless you're building an API, chances are :class:`~flask_unchained.Controller` is the base class you want to extend. Controllers include a bit of magic that deserves some explanation:

On any Controller subclass that doesn't specify itself as abstract, all methods not designated as protected by prefixing them with an ``_`` are automatically assigned default routing rules. In the example below, ``foo_baz`` has a route decorator, but ``foo`` and ``foo_bar`` do not. The undecorated views will be assigned default route rules of ``/foo`` and ``/foo-bar`` respectively (the default is to convert the method name to kebab-case).

.. code:: python

   # your_bundle/views.py

   from flask_unchained import Controller, route

   class MyController(Controller):
      def foo():
         return self.render('foo')

      def foo_bar():
         return self.render('foo_bar')

      @route('/foobaz')
      def foo_baz():
         return self.render('foo_baz')

      def _protected_function():
         return 'stuff'

Controller Meta Options
#######################

Controllers have a few meta options that you can use to customize their behavior:

.. code:: python

   # your_bundle/views.py

   from flask_unchained import Controller, route

   class SiteController(Controller):
       class Meta:
           abstract: bool = False                         # default is False
           decorators: List[callable] = ()                # default is an empty tuple
           template_folder: str = 'site'                  # see explanation below
           template_file_extension: Optional[str] = None  # default is None
           url_prefix = Optional[str] = None              # default is None
           endpoint_prefix = 'site_controller'            # see explanation below

.. list-table::
   :header-rows: 1

   * - meta option name
     - description
     - default value
   * - abstract
     - Whether or not this controller should be abstract. Abstract controller classes do not get any routes assigned to their view methods (if any exist).
     - False
   * - decorators
     - A list of decorators to apply to all views in this controller.
     - ()
   * - template_folder
     - The name of the folder containing the templates for this controller's views.
     - Defaults to the snake_cased class name (with the ``Controller`` or ``View`` suffixes stripped).
   * - template_file_extension
     - The filename extension to use for templates for this controller's views.
     - Defaults to your app config's ``TEMPLATE_FILE_EXTENSION`` setting, and overrides it if set.
   * - url_prefix
     - The url prefix to use for all routes from this controller.
     - Defaults to ``'/'`` (aka no prefix).
   * - endpoint_prefix
     - The endpoint prefix to use for all routes from this controller.
     - Defaults to the snake_cased class name.

Overriding Controllers
######################

Controllers can be extended or overridden by creating an equivalently named class higher up in the bundle hierarchy. (In other words, either in a bundle that extends another bundle, or in your app bundle.) As an example, the security bundle includes :class:`~flask_unchained.bundles.security.SecurityController`. To extend it, you would simply subclass it like any other class in Python and change what you need to:

.. code:: python

   # your_app_or_security_bundle/views.py

   from flask_unchained.bundles.security import SecurityController as BaseSecurityController

   # to extend BaseSecurityController
   class SecurityController(BaseSecurityController):
       pass

   # to completely override it, just use the same name without extending the base class
   class SecurityController:
       pass

Resource
""""""""

The :class:`~flask_unchained.Resource` class extends :class:`~flask_unchained.Controller` to add support for building RESTful APIs. It adds a bit of magic around specific methods:

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - HTTP Method
     - Resource class method name
     - URL Rule
   * - GET
     - list
     - /
   * - POST
     - create
     - /
   * - GET
     - get
     - /<cls.Meta.member_param>
   * - PATCH
     - patch
     - /<cls.Meta.member_param>
   * - PUT
     - put
     - /<cls.Meta.member_param>
   * - DELETE
     - delete
     - /<cls.Meta.member_param>

If you implement any of these methods, then the shown URL rules will automatically be used.

So, for example::

    from http import HTTPStatus
    from flask_unchained import Resource, injectable, param_converter, request
    from flask_unchained.bundles.security import User, UserManager


    class UserResource(Resource):
        class Meta:
            url_prefix = '/users'
            member_param = '<int:id>'
            unique_member_param = '<int:user_id>'

        user_manager: UserManager = injectable

        def list():
            return self.jsonify(dict(users=self.user_manager.all()))

        def create():
            data = request.get_json()
            user = self.user_manager.create(**data, commit=True)
            return self.jsonify(dict(user=user), code=HTTPStatus.CREATED)

        @param_converter(id=User)
        def get(user):
            return self.jsonify(dict(user=user)

        @param_converter(id=User)
        def patch(user):
            data = request.get_json()
            user = self.user_manager.update(user, **data, commit=True)
            return self.jsonify(dict(user=user))

        @param_converter(id=User)
        def put(user):
            data = request.get_json()
            user = self.user_manager.update(user, **data, commit=True)
            return self.jsonify(dict(user=user))

        @param_converter(id=User)
        def delete(user):
            self.user_manager.delete(user, commit=True)
            return self.make_response('', code=HTTPStatus.NO_CONTENT)

Registered like so::

  routes = lambda: [
      resource(UserResource),
  ]

Results in the following routes::

   GET     /users             UserResource.list
   POST    /users             UserResource.create
   GET     /users/<int:id>    UserResource.get
   PATCH   /users/<int:id>    UserResource.patch
   PUT     /users/<int:id>    UserResource.put
   DELETE  /users/<int:id>    UserResource.delete

Resource Meta Options
#####################

Resources have a few extra meta options on top of those that Controller includes:

.. code:: python

   # your_bundle/views.py

   from flask_unchained import Controller, route

   class UserResource(Resource):
       class Meta:
           abstract: bool = False                     # the default
           decorators: List[callable] = ()            # the default
           url_prefix = Optional[str] = '/users'      # automatically determined
           member_param: str = '<int:id>'             # the default
           unique_member_parm: str = '<int:user_id>'  # automatically determined

.. list-table::
   :header-rows: 1

   * - meta option name
     - description
     - default value
   * - :attr:`~flask_unchained.Resource.Meta.url_prefix`
     - The url prefix to use for all routes from this resource.
     - Defaults to the pluralized, kebab-cased class name (without the Resource suffix)
   * - :attr:`~flask_unchained.Resource.Meta.member_param`
     - The url parameter rule to use for the special member functions (``get``, ``patch``, ``put``, and ``delete``) of this resource.
     - ``<int:id>``
   * - :attr:`~flask_unchained.Resource.Meta.unique_member_param`
     - The url parameter rule to use for the special member methods (``get``, ``patch``, ``put``, and ``delete``) of this resource when :attr:`~flask_unchained.Resource.Meta.member_param` conflicts with a subresource's :attr:`~flask_unchained.Resource.Meta.member_param`.
     - ``<{type}:{prefix}_{name}>`` where ``type`` and ``name`` come from ``member_param`` and ``prefix`` is the snake_cased class name (without the Resource suffix)

Overriding Resources
####################

Because :class:`~flask_unchained.Resource` is already a subclass of :class:`~flask_unchained.Controller`, overriding resources works the same way as for controllers.

Templating
""""""""""

Flask Unchained uses the `Jinja <https://jinja.palletsprojects.com/en/2.10.x/templates/>`_ templating language, just like stock Flask.

By default bundles are configured to use a ``templates`` subfolder. This is configurable by setting the ``template_folder`` attribute on your ``Bundle`` subclass to a custom path.

Controllers each have their own template folder within ``Bundle.template_folder``. It defaults to the snake_cased class name, with the suffixes ``Controller`` or ``View`` stripped (if any). You can customize it using :attr:`flask_unchained.Controller.Meta.template_folder`.

The default file extension used for templates is configured by setting ``TEMPLATE_FILE_EXTENSION`` in your app config. It defaults to ``.html``, and is also configurable on a per-controller basis by setting :attr:`flask_unchained.Controller.Meta.template_file_extension`.

Taking the above into account, given the following controller:

.. code:: python

   class SiteController(Controller):
       @route('/')
       def index():
           return self.render('index')

Then the corresponding folder structure would look like this:

.. code:: bash

   ./your_bundle
   ├── templates
   │   └── site
   │       └── index.html
   ├── __init__.py
   └── views.py

Extending and Overriding Templates
""""""""""""""""""""""""""""""""""

Templates can be overridden by placing an equivalently named template higher up in the bundle hierarchy.

So for example, the Security Bundle includes default templates for all of its views. They are located at ``security/login.html``, ``security/register.html``, and so on. Thus, to extend or override them, you would make a ``security`` folder in your app bundle's ``templates`` folder and put your customized templates with the same names in it. You can even extend the template you're overriding, using the standard Jinja syntax (this doesn't work in regular Flask apps):

.. code:: html+jinja

   {# your_app_or_security_bundle/templates/security/login.html #}

   {% extends 'security/login.html' %}

   {% block content %}
      <h1>Login</h1>
      {{ render_form(login_user_form, endpoint='security_controller.login') }}
   {% endblock %}

If you encounter problems, you can set the ``EXPLAIN_TEMPLATE_LOADING`` config option to ``True`` to help debug what's going on.

Dependency Injection
""""""""""""""""""""

Controllers are configured with dependency injection set up on them automatically. You can use class attributes or the constructor (or both).

Here's an example of using class attributes::

   from flask_unchained import Controller, injectable
   from flask_unchained.bundles.security import Security, SecurityService, SecurityUtilsService
   from flask_unchained.bundles.sqlalchemy import SessionManager

   class SecurityController(Controller):
       security: Security = injectable
       security_service: SecurityService = injectable
       security_utils_service: SecurityUtilsService = injectable
       session_manager: SessionManager = injectable

And here's what the same thing using the constructor looks like::

   from flask_unchained import Controller, injectable
   from flask_unchained.bundles.security import Security, SecurityService, SecurityUtilsService
   from flask_unchained.bundles.sqlalchemy import SessionManager

   class SecurityController(Controller):
       def __init__(self,
                    security: Security = injectable,
                    security_service: SecurityService = injectable,
                    security_utils_service: SecurityUtilsService = injectable,
                    session_manager: SessionManager = injectable):
           self.security = security
           self.security_service = security_service
           self.security_utils_service = security_utils_service
           self.session_manager = session_manager

API Docs
^^^^^^^^

See :doc:`../api/controller-bundle`
