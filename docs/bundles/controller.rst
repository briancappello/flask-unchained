Controller Bundle
-----------------

The controller bundle provides the primary means for defining and registering views and their routes in Flask Unchained.

Installation
^^^^^^^^^^^^

The controller bundle comes enabled by default.

Config
^^^^^^

.. automodule:: flask_unchained.bundles.controller.config
   :members:
   :noindex:

Usage
^^^^^

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
   :widths: 15 85

   * - Function
     - Description
   * - :func:`~flask_unchained.controller`
     - Registers a controller and its views with the app, optionally customizing the routes to register.
   * - :func:`~flask_unchained.resource`
     - Registers a resource and its views with the app, optionally customizing the routes to register.
   * - :func:`~flask_unchained.func`
     - Registers a function-based view with the app, optionally specifying the routing rules.
   * - :func:`~flask_unchained.include`
     - Includes all of the routing rules from the specified module at that point in the tree.
   * - :func:`~flask_unchained.prefix`
     - Prefixes all of the child routing rules with the given prefix.
   * - :func:`~flask_unchained.delete`
     - Defines a controller/resource method as only accepting the HTTP ``DELETE`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.get`
     - Defines a controller/resource method as only accepting the HTTP ``GET`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.patch`
     - Defines a controller/resource method as only accepting the HTTP ``PATCH`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.post`
     - Defines a controller/resource method as only accepting the HTTP ``POST`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.put`
     - Defines a controller/resource method as only accepting the HTTP ``PUT`` method, otherwise the same as :func:`~flask_unchained.rule`.
   * - :func:`~flask_unchained.rule`
     - Define customizations to a controller/resource method's route rules.

Class-Based Views
~~~~~~~~~~~~~~~~~

The controller bundle includes two base classes that all of your views should extend. They are :class:`~flask_unchained.Controller` and :class:`~flask_unchained.Resource`:

Controller
""""""""""

Unless you're building an API, chances are :class:`~flask_unchained.Controller` is the base class you want to extend. Controllers include a bit of magic that deserves some explanation:

On any Controller subclass that doesn't specify itself as abstract, all methods not designated as protected by prefixing them with an ``_`` are automatically assigned default routing rules. In the example below, ``foo_baz`` has a route decorator, but ``foo`` and ``foo_bar`` do not. The undecorated views will be assigned default route rules of ``/foo`` and ``/foo-bar`` respectively (the default is to convert the method name to kebab-case).

.. code:: python

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

Overriding Controllers
""""""""""""""""""""""

Controllers can be extended or overridden by creating an equivalently named subclass higher up in the bundle hierarchy. (In other words, either in a bundle that extends another bundle, or in your app bundle.) As an example, the security bundle includes :class:`~flask_unchained.bundles.security.SecurityController`. To extend it, you would simply subclass it like any other class in Python and change what you need to:

.. code:: python

   # your_app_or_security_bundle/views.py

   from flask_unchained.bundles.security import SecurityController as BaseSecurityController

   class SecurityController(BaseSecurityController):
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
     - /<cls.member_param>
   * - PATCH
     - patch
     - /<cls.member_param>
   * - PUT
     - put
     - /<cls.member_param>
   * - DELETE
     - delete
     - /<cls.member_param>

If you implement any of these methods, then the shown URL rules will automatically be used.

So, for example::

        from flask_unchained import Resource, injectable, param_converter
        from flask_unchained.bundles.security import User, UserManager


        class UserResource(Resource):
            class Meta:
                member_param: '<string:username>'

            def __init__(self, user_manager: UserManager = injectable):
                super().__init__()
                self.user_manager = user_manager

            def list():
                return self.jsonify(dict(users=User.query.all()))

            def create():
                user = self.user_manager.create(**data, commit=True)
                return self.jsonify(dict(user=user), code=201)

            @param_converter(username=User)
            def get(user):
                return self.jsonify(dict( user=user)

            @param_converter(username=User)
            def patch(user):
                user = self.user_manager.update(user, **data, commit=True)
                return self.jsonify(dict(user=user))

            @param_converter(username=User)
            def put(user):
                user = self.user_manager.update(user, **data, commit=True)
                return self.jsonify(dict(user=user))

            @param_converter(username=User)
            def delete(user):
                self.user_manager.delete(user, commit=True)
                return self.make_response('', code=204)

Registered like so::

  routes = lambda: [
      resource('/users', UserResource),
  ]

Would register the following routes::

   GET     /users                      UserResource.list
   POST    /users                      UserResource.create
   GET     /users/<string:username>    UserResource.get
   PATCH   /users/<string:username>    UserResource.patch
   PUT     /users/<string:username>    UserResource.put
   DELETE  /users/<string:username>    UserResource.delete

Because :class:`~flask_unchained.Resource` is already a subclass of :class:`~flask_unchained.Controller`, overriding resources works the same way as for controllers.

Templating
""""""""""

Flask Unchained uses the Jinja templating language, just like stock Flask.

By default bundles are configured to use a `templates` subfolder. This is configurable by setting :attr:`flask_unchained.Bundle.template_folder` to a custom path.

Controllers each have their own template folder within ``Bundle.template_folder``. It defaults to :python:`snake_case(right_replace(ControllerClass.__name__, 'Controller', ''))` and is configurable by setting :attr:`flask_unchained.Controller.Meta.template_folder_name`.

The default file extension used for templates is configured by setting ``TEMPLATE_FILE_EXTENSION``. It defaults to `.html`, and is also configurable on a per-controller basis by setting :attr:`flask_unchained.Controller.Meta.template_file_extension`.

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

Overriding Templates
""""""""""""""""""""

Templates can be overridden by placing an equivalently named template higher up in the bundle hierarchy.

So for example, the security bundle includes default templates for all of its views. They are located at ``security/login.html``, ``security/logout.html``, ``security/register.html``, and so on. Thus, to extend or override them, you would make a ``security`` folder in your app bundle's or your security bundle's ``templates`` folder and put your customized ``login.html`` template in it. Flask Unchained will do the rest to make sure it uses the one you wanted. It's also worth noting that can even extend the template you're overriding, using the standard Jinja syntax (this doesn't work in stock Flask apps):

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

Controllers are configured with dependency injection set up on their constructors automatically. Here's an example of what it looks like::

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

By setting the default value of an argument to :attr:`flask_unchained.injectable`, we are informing the :class:`~flask_unchained.Unchained` extension that it should inject that argument. Services and extensions are automatically dependency-injectable by default, and by using the :meth:`flask_unchained.Unchained.service` decorator or the :meth:`flask_unchained.Unchained.register_service` method, you can register anything else you might want to as injectable.

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/controller`
