.. BEGIN setup/comments -------------------------------------------------------

   The heading hierarchy is defined as:
        h1: =
        h2: -
        h3: ^
        h4: ~
        h5: "
        h6: #

.. BEGIN document -------------------------------------------------------------

Introducing Flask Unchained
===========================

**Flask Unchained is a Flask extension, a pluggable implementation of the application factory pattern, and a set of mostly optional "bundles" that together create a modern, fully integrated, and highly customizable web framework** :bolditalic:`for` **Flask and its extension ecosystem.** Flask Unchained aims to stay true to the spirit and API of Flask, while making it significantly easier to quickly build large/complex web apps and GraphQL/REST APIs with Flask and SQLAlchemy.

Bundles are a powerful concept Flask Unchained introduces to Flask: Bundles are Python packages that integrate functionality with Flask, Flask Unchained, and other bundles. That could mean anything from integrating Flask extensions to being full-blown apps *your* app can integrate, customize, and extend (like say, a blog or a web store).

Conceptually, a bundle *is* a blueprint, and Flask Unchained gives you complete control to configure not only which views from each bundle get registered with your app and at what routes, but also to extend and/or override anything else you might want to from the bundles you enable.

Some examples of what you can customize from bundles include configuration, controllers, resources, and routes, templates, extensions and services, and models and serializers. Each uses simple and consistent patterns that work the same way across every bundle. Extended/customized bundles can themselves also be distributed as their own projects, and support the same patterns for customization, ad infinitum.

.. admonition:: Included bundles & integrated extensions
    :class: tip

    - **Controller Bundle**: Enhanced class-based views, declarative routing, and `Flask WTF <https://flask-wtf.readthedocs.io/en/stable/>`_ for forms and CSRF protection.
    - **SQLAlchemy Bundle** `Flask SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>`_ and `Flask Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_ for `SQLAlchemy <https://www.sqlalchemy.org/>`_ models, plus some optional "sugar" on top of SQLAlchemy to make the best ORM in existence even quicker and easier to use.
    - **Security Bundle**: `Flask Login <https://flask-login.readthedocs.io/en/latest/>`_ for authentication and `Flask Principal <https://pythonhosted.org/Flask-Principal/>`_ for authorization.
    - **API Bundle**: RESTful APIs with `Flask Marshmallow <https://flask-marshmallow.readthedocs.io/en/latest/>`_ serializers for SQLAlchemy models.
    - **Graphene Bundle**: `Flask GraphQL <https://github.com/graphql-python/flask-graphql>`_ with `Graphene <https://docs.graphene-python.org/en/latest/quickstart/>`_ for SQLAlchemy models.
    - **Celery Bundle**: `Celery <http://www.celeryproject.org/>`_ distributed tasks queue.
    - `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_, `Flask BabelEx <https://pythonhosted.org/Flask-BabelEx/>`_, `Flask Mail <https://pythonhosted.org/Flask-Mail/>`_, `Flask Session <https://pythonhosted.org/Flask-Session/>`_, ...
    - **Testing** with `pytest <https://docs.pytest.org/en/latest/>`_ and `factory_boy <https://factoryboy.readthedocs.io/en/latest/>`_ supported out-of-the-box.

.. admonition:: Thanks and acknowledgements
    :class: tip

    The architecture of how Flask Unchained and its bundles work is inspired by the `Symfony Framework <https://symfony.com>`_, which is awesome, aside from the fact that it isn't Python ;)

Install Flask Unchained
-----------------------

Requires **Python 3.6+**

.. code:: shell

    pip install "flask-unchained[dev]"

Hello World
-----------

Flask Unchained apps can grow to be as big as you like, or as small:

.. code-block::

    # project-root/app.py

    import random
    from flask_unchained import AppBundle, Service, injectable
    from flask_unchained import Controller, route, param_converter, url_for

    class App(AppBundle):
        pass

    BUNDLES = ['flask_unchained.bundles.controller']

    class NameService(Service):
        NAMES = ['Alice', 'Bob', 'Grace', 'Judy']

        def get_random(self) -> str:
            return random.choice(self.NAMES)

    class SiteController(Controller):
        name_service: NameService = injectable

        @route('/')
        def index(self):
            hello_url = url_for('site_controller.hello', name='World')
            return f'<a href="{hello_url}">Hello World</a>'

        @route('/hello')
        @param_converter(name=str)
        def hello(self, name: str = None):
            name = name or self.name_service.get_random()
            return f'Hello {name} from Flask Unchained!'

    class TestSiteController:
        def test_index(self, client):
            r = client.get('site_controller.index')
            assert r.status_code == 200
            assert "Hello World" in r.html

        def test_hello(self, client):
            r = client.get(url_for('site_controller.hello', name='Hello'))
            assert r.status_code == 200
            assert r.html == 'Hello Hello from Flask Unchained!'

That's it! Let's fire this bad boy up:

.. code:: shell

    cd project-root
    export UNCHAINED_CONFIG="app"
    pytest app.py
    flask run

You may be wondering, what happened to the ``Flask`` app instance? We are literally unchained from it! The ``pytest`` and ``flask`` commands use the included app factory to automatically initialize and "boot up" the ``Flask`` instance for you. **No plumbing, no boilerplate, everything just works.** In production, you call the app factory yourself, like so:

.. code-block::

    # project-root/wsgi.py

    import os
    from flask_unchained import AppFactory, PROD

    app = AppFactory().create_app(os.getenv('FLASK_ENV', PROD))

The app factory might sound like magic, but it's actually quite easy to understand, and every step it takes can be customized if necessary. In pseudo code, it looks about like this:

.. code-block::

    class AppFactory:
        def create_app(self, env):
            # first load the user's unchained config
            unchained_config = self.load_unchained_config(env)

            # next load configured bundles and the user's app bundle
            app_bundle, bundles = self.load_bundles(unchained_config.BUNDLES)

            # instantiate the Flask app instance
            app = Flask(app_bundle.name, **kwargs_from_unchained_config)

            # let bundles configure the app pre-initialization
            for bundle in bundles:
                bundle.before_init_app(app)

            # discover code from bundles and boot up the Flask app using hooks
            unchained.init_app(app, bundles)
                # the Unchained extension runs hooks in their correct order:
                RegisterExtensionsHook.run_hook(app, bundles)
                ConfigureAppHook.run_hook(app, bundles)
                InitExtensionsHook.run_hook(app, bundles)
                RegisterServicesHook.run_hook(app, bundles)
                RegisterCommandsHook.run_hook(app, bundles)
                RegisterRoutesHook.run_hook(app, bundles)
                RegisterBundleBlueprintsHook.run_hook(app, bundles)
                # (there may be more depending on which bundles you enable)

            # let bundles configure the app post-initialization
            for bundle in bundles:
                bundle.after_init_app(app)

            # return the finalized app ready to rock'n'roll
            return app

Continue reading to learn more about Flask Unchained's features, or check out :doc:`how-flask-unchained-works` for a deeper look at the app factory.

.. admonition:: This is beta software
    :class: warning

    The core should be solid, but there will be bugs at the edges. Please file `issues on GitHub <https://github.com/briancappello/flask-unchained/issues>`_ if you encounter any problems or have any questions!

Going Big (Project Layout)
--------------------------

When you want to expand beyond a single file, Flask Unchained defines a configurable folder structure for you so that everything just works. A common structure might look like this:

.. code-block:: shell

    /home/user/dev/project-root
    ├── unchained_config.py # the Flask Unchained config
    ├── app                 # your App Bundle package
    │   ├── admins          # Flask-Admin model admins
    │   ├── commands        # Click CLI groups/commands
    │   ├── extensions      # Flask extensions
    │   ├── models          # SQLAlchemy models
    │   ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
    │   ├── serializers     # Marshmallow serializers (aka schemas)
    │   ├── services        # dependency-injectable Services
    │   ├── tasks           # Celery tasks
    │   ├── templates       # Jinja2 templates
    │   ├── views           # Controllers, Resources and ModelResources
    │   ├── __init__.py
    │   ├── config.py       # your app config
    │   └── routes.py       # declarative routes
    ├── bundles             # custom bundles and/or bundle extensions/overrides
    │   └── security        # a customized/extended Security Bundle
    │       ├── models
    │       ├── serializers
    │       ├── services
    │       ├── templates
    │       └── __init__.py
    ├── db
    │   └── migrations      # migrations generated by Flask-Migrate
    ├── static              # the top-level static assets folder
    ├── templates           # the top-level templates folder
    └── tests               # your pytest tests

Read on to learn more about Flask Unchained's features and how it all works, or check out the :ref:`tutorial` to start building now!

Features
--------

Bundles
^^^^^^^

Bundle Structure
~~~~~~~~~~~~~~~~

The example "hello world" app bundle lived in a single file, while a "full" bundle package consists of many modules. An example using the defaults looks like this:

.. code-block:: shell

    /home/user/dev/project-root
    └── your_cool_bundle    # a bundle package
        ├── admins          # Flask-Admin model admins
        ├── commands        # Click CLI groups/commands
        ├── extensions      # Flask extensions
        ├── hooks           # app factory hooks, if needed
        ├── models          # SQLAlchemy models
        ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
        ├── serializers     # Marshmallow serializers (aka schemas)
        ├── services        # dependency-injectable services
        ├── tasks           # Celery tasks
        ├── templates       # Jinja2 templates
        ├── views           # Controllers, Resources and views
        ├── __init__.py     # the Bundle subclass
        ├── config.py       # bundle config
        └── routes.py       # declarative routes

These module locations are customizable on a per-bundle basis by setting class attributes on your :class:`~flask_unchained.bundles.Bundle` subclass, for example:

.. code-block::

    # your_custom_bundle/__init__.py

    from flask_unchained import Bundle

    class YourCustomBundle(Bundle):
        config_module_name = 'settings'
        routes_module_name = 'urls'
        views_module_names = ['controllers', 'resources', 'views']

You can see the default module names and the override attribute names to set on your :class:`~flask_unchained.bundles.Bundle` subclass by printing the ordered list of hooks that will run for your app using ``flask unchained hooks``:

.. code-block:: shell

    flask unchained hooks

    Hook Name             Default Bundle Module  Bundle Module Override Attr
    -------------------------------------------------------------------------
    register_extensions   extensions             extensions_module_names
    models                models                 models_module_names
    configure_app         config                 config_module_name
    init_extensions       extensions             extensions_module_names
    services              services               services_module_names
    commands              commands               commands_module_names
    routes                routes                 routes_module_name
    bundle_blueprints     (None)                 (None)
    blueprints            views                  blueprints_module_names
    views                 views                  views_module_names
    model_serializers     serializers            model_serializers_module_names
    model_resources       views                  model_resources_module_names
    celery_tasks          tasks                  celery_tasks_module_names

Bundle Blueprints
~~~~~~~~~~~~~~~~~

Bundles *are* blueprints, so if you want to define request/response functions that should only run for views from a specific bundle, you can do that like so:

.. code-block::

    from flask_unchained import Bundle, unchained

    class YourCoolBundle(Bundle):
        name = 'your_cool_bundle'  # the default (snake_cased class name)

    @unchained.your_cool_bundle.before_request
    def this_only_runs_before_requests_to_views_from_your_cool_bundle():
        pass

    # the other supported decorators are also available:
    @unchained.your_cool_bundle.after_request
    @unchained.your_cool_bundle.teardown_request
    @unchained.your_cool_bundle.context_processor
    @unchained.your_cool_bundle.url_defaults
    @unchained.your_cool_bundle.url_value_preprocessor
    @unchained.your_cool_bundle.errorhandler

The API here is the same as :class:`flask.Blueprint`, however, its methods must be accessed via the :class:`~flask_unchained.unchained.Unchained` extension. The syntax is ``@unchained.bundle_name.blueprint_method_name``.

.. admonition:: Wait but why?
    :class: warning

    Sadly, there are some very serious technical limitations with the implementation of :class:`flask.Blueprint` such that its direct usage breaks the power and flexibility of Flask Unchained. Under the hood, Flask Unchained does indeed use an instance of :class:`flask.Blueprint` for each bundle - you just never interact with them directly.

    You can *technically* continue using :class:`flask.Blueprint` **strictly for views in your app bundle**, however this support is only kept around for porting purposes. Note that even in your app bundle, views from blueprints unfortunately will not work with declarative routing.

Extending and Overriding Bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extending and overriding bundles is pretty simple. All you need to do is subclass the bundle you want to extend in its own Python package, and include that package in your ``unchained_config.BUNDLES`` instead of the original bundle. There is no limit to the depth of the bundle hierarchy (other than perhaps your sanity). So, for example, to extend the Security Bundle, it would look like this:

.. code:: python

   # project-root/bundles/security/__init__.py

   from flask_unchained.bundles.security import SecurityBundle as BaseSecurityBundle

   class SecurityBundle(BaseSecurityBundle):
       pass

.. code:: python

   # project-root/unchained_config.py

   BUNDLES = [
       # ...
       'bundles.security',
       'app',
   ]

The App Bundle
~~~~~~~~~~~~~~

When defining the app bundle, you must subclass :class:`~flask_unchained.bundles.AppBundle` instead of :class:`~flask_unchained.bundles.Bundle`:

.. code-block::

    # project-root/app/__init__.py

    from flask_unchained import AppBundle

    class App(AppBundle):
        pass

Everything about your app bundle is otherwise the same as for regular bundles, except **the app bundle can extend and/or override anything from any bundle**.

Controllers and Templates
^^^^^^^^^^^^^^^^^^^^^^^^^

The controller bundle includes two base classes that all of your views should extend. The first is :class:`~flask_unchained.Controller`, which under the hood is actually very similar to :class:`flask.views.View`, however, they're not compatible. The second is :class:`~flask_unchained.Resource`, which extends :class:`~flask_unchained.Controller`, and whose implementation draws much inspiration from `Flask-RSETful <https://flask-restful.readthedocs.io/en/latest/>`_ (specifically, the `Resource <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L543>`_ and `Api <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L38>`_ classes).

Controller
~~~~~~~~~~

Chances are :class:`~flask_unchained.Controller` is the base class you want to extend, unless you're building a RESTful API. Controllers include a bit of magic:

.. code:: python

   # your_bundle/views.py

   from flask_unchained import Controller, route, injectable

    class SiteController(Controller):
        # all of class Meta is optional (automatic defaults shown)
        class Meta:
            abstract: bool = False
            url_prefix = Optional[str] = '/'          # aka no prefix
            endpoint_prefix: str = 'site_controller'  # snake_cased class name
            template_folder: str = 'site'             # snake_cased class name prefix
            template_file_extension: Optional[str] = '.html'
            decorators: List[callable] = ()

        # controllers automatically support dependency injection
        name_service: NameService = injectable

        @route('/foobaz', methods=['GET', 'POST'])
        def foo_baz():
            # template paths can be explicit
            return self.render('site/foo_baz.html')

        def view_one():
            # or just the filename
            return self.render('one')  # equivalent to 'site/one.html'

        def view_two():
            return self.render('two')

        def _protected_function():
            return 'not a view'

On any subclass of ``Controller`` that isn't abstract, all public methods are automatically assigned default routing rules. In the example above, ``foo_baz`` has a route decorator, but ``view_one`` and ``view_two`` do not. The undecorated views will be assigned default routing rules of ``/view-one`` and ``/view-two`` respectively (the default is to convert the method name to kebab-case). Protected methods (those prefixed with ``_``) are not assigned routes.

Templates
~~~~~~~~~

Flask Unchained uses the `Jinja <https://jinja.palletsprojects.com/en/2.10.x/templates/>`_ templating language, just like Flask.

By default bundles are configured to use a ``templates`` subfolder. This is customizable per-bundle:

.. code-block::

    # your_bundle/__init__.py

    from flask_unchained import Bundle

    class YourBundle(Bundle):
        template_folder = 'templates'  # the default

Controllers each have their own template folder within :attr:`Bundle.template_folder`. It defaults to the snake_cased class name, with the suffixes ``Controller`` or ``View`` stripped (if any). You can customize it using :attr:`Controller.Meta.template_folder`.

The default file extension used for templates is configured by setting ``TEMPLATE_FILE_EXTENSION`` in your app config. It defaults to ``.html``, and is also configurable on a per-controller basis by setting :attr:`Controller.Meta.template_file_extension`.

Therefore, the above controller corresponds to the following templates folder structure:

.. code-block:: shell

   ./your_bundle
   ├── templates
   │   └── site
   │       ├── foo_baz.html
   │       ├── one.html
   │       └── two.html
   ├── __init__.py
   └── views.py

Extending and Overriding Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Templates can be overridden by placing an equivalently named template higher up in the bundle hierarchy (i.e. in a bundle extending another bundle, or in your app bundle).

So for example, the Security Bundle includes default templates for all of its views. They are located at ``security/login.html``, ``security/register.html``, and so on. Thus, to override them, you would make a ``security`` folder in your app bundle's ``templates`` folder and put your customized templates with the same names in it. You can even extend the template you're overriding, using the standard Jinja syntax (this doesn't work in regular Flask apps):

.. code:: django

   {# your_app_or_security_bundle/templates/security/login.html #}

   {% extends 'security/login.html' %}

   {% block content %}
      <h1>Login</h1>
      {{ render_form(login_user_form, endpoint='security_controller.login') }}
   {% endblock %}

If you encounter problems, you can set the ``EXPLAIN_TEMPLATE_LOADING`` config option to ``True`` to help debug what's going on.

Resources (API Controllers)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`~flask_unchained.Resource` class extends :class:`~flask_unchained.Controller` to add support for building RESTful APIs. It adds a bit of magic around specific methods:

.. list-table::
   :header-rows: 1

   * - Method name on your Resource subclass
     - HTTP Method
     - URL Rule
   * - list
     - GET
     - /
   * - create
     - POST
     - /
   * - get
     - GET
     - /<cls.Meta.member_param>
   * - patch
     - PATCH
     - /<cls.Meta.member_param>
   * - put
     - PUT
     - /<cls.Meta.member_param>
   * - delete
     - DELETE
     - /<cls.Meta.member_param>

If you implement any of these methods, then the shown URL rules will automatically be used.

So, for example::

    from http import HTTPStatus
    from flask_unchained import Resource, injectable, param_converter, request
    from flask_unchained.bundles.security import User, UserManager

    class UserResource(Resource):
        # class Meta is optional on resources (automatic defaults shown)
        class Meta:
            url_prefix = '/users'
            member_param = '<int:id>'
            unique_member_param = '<int:user_id>'

        # resources are controllers, so they support dependency injection
        user_manager: UserManager = injectable

        def list():
            return self.jsonify(dict(users=self.user_manager.all()))
            # NOTE: returning SQLAlchemy models directly like this is
            # only supported by ModelResource from the API Bundle

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

Declarative Routing
^^^^^^^^^^^^^^^^^^^

Using declarative routing, your app bundle has final say over which views (from all bundles) should get registered with the app, as well as their routing rules. By default, it uses the rules decorated on views:

.. code-block::

    # project-root/app/routes.py

    from flask_unchained import (controller, resource, func, include, prefix,
                                 delete, get, patch, post, put, rule)

    from flask_unchained.bundles.security import SecurityController

    from .views import SiteController

    routes = lambda: [
        controller(SiteController),
        controller(SecurityController),
    ]

By running ``flask urls``, we can verify it does what we want:

.. code-block:: shell

    flask urls
    Method(s)  Rule                     Endpoint                    View
    ---------------------------------------------------------------------------------------------------------------------------------
          GET  /static/<path:filename>  static                      flask.helpers.send_static_file
          GET  /                        site_controller.index       app.views.SiteController.index
          GET  /hello                   site_controller.hello       app.views.SiteController.hello
    GET, POST  /login                   security_controller.login   flask_unchained.bundles.security.views.SecurityController.login
          GET  /logout                  security_controller.logout  flask_unchained.bundles.security.views.SecurityController.logout

Declarative routing can also be *much* more powerful when you want it to be. For example, to build a RESTful SPA with the Security Bundle, your routes might look like this:

.. code-block::

    # project-root/app/routes.py

    from flask_unchained import (controller, resource, func, include, prefix,
                                 delete, get, patch, post, put, rule)

    from flask_unchained.bundles.security import SecurityController, UserResource

    from .views import SiteController

    routes = lambda: [
        controller(SiteController),

        controller('/auth', SecurityController, rules=[
            get('/reset-password/<token>', SecurityController.reset_password,
                endpoint='security_api.reset_password'),
        ]),
        prefix('/api/v1', [
            controller('/auth', SecurityController, rules=[
                get('/check-auth-token', SecurityController.check_auth_token,
                    endpoint='security_api.check_auth_token', only_if=True),
                post('/login', SecurityController.login,
                     endpoint='security_api.login'),
                get('/logout', SecurityController.logout,
                    endpoint='security_api.logout'),
                post('/send-confirmation-email',
                     SecurityController.send_confirmation_email,
                     endpoint='security_api.send_confirmation_email'),
                post('/forgot-password', SecurityController.forgot_password,
                     endpoint='security_api.forgot_password'),
                post('/reset-password/<token>', SecurityController.reset_password,
                     endpoint='security_api.post_reset_password'),
                post('/change-password', SecurityController.change_password,
                     endpoint='security_api.change_password'),
            ]),
            resource('/users', UserResource),
        ]),
    ]

Which results in the following:

.. code-block:: shell

    flask urls
    Method(s)  Rule                                  Endpoint                              View
    ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          GET  /static/<path:filename>               static                                flask.helpers.send_static_file
          GET  /                                     site_controller.index                 app.views.SiteController.index
          GET  /hello                                site_controller.hello                 app.views.SiteController.hello
          GET  /auth/reset-password/<token>          security_api.reset_password           flask_unchained.bundles.security.views.SecurityController.reset_password
          GET  /api/v1/auth/check-auth-token         security_api.check_auth_token         flask_unchained.bundles.security.views.SecurityController.check_auth_token
         POST  /api/v1/auth/login                    security_api.login                    flask_unchained.bundles.security.views.SecurityController.login
          GET  /api/v1/auth/logout                   security_api.logout                   flask_unchained.bundles.security.views.SecurityController.logout
         POST  /api/v1/auth/send-confirmation-email  security_api.send_confirmation_email  flask_unchained.bundles.security.views.SecurityController.send_confirmation_email
         POST  /api/v1/auth/forgot-password          security_api.forgot_password          flask_unchained.bundles.security.views.SecurityController.forgot_password
         POST  /api/v1/auth/reset-password/<token>   security_api.post_reset_password      flask_unchained.bundles.security.views.SecurityController.reset_password
         POST  /api/v1/auth/change-password          security_api.change_password          flask_unchained.bundles.security.views.SecurityController.change_password
         POST  /api/v1/users                         user_resource.create                  flask_unchained.bundles.security.views.UserResource.create
          GET  /api/v1/users/<int:id>                user_resource.get                     flask_unchained.bundles.security.views.UserResource.get
        PATCH  /api/v1/users/<int:id>                user_resource.patch                   flask_unchained.bundles.security.views.UserResource.patch

Here is a summary of the functions imported at the top of the ``routes.py`` module:

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
   * - :func:`~flask_unchained.get`, :func:`~flask_unchained.patch`, :func:`~flask_unchained.post`, :func:`~flask_unchained.put`, and :func:`~flask_unchained.delete`
     - Like :func:`~flask_unchained.rule` except specifically for each HTTP method.

Dependency Injection
^^^^^^^^^^^^^^^^^^^^

Flask Unchained supports dependency injection of services and extensions (by default).

Services
~~~~~~~~

For services to be automatically discovered, they must subclass :class:`~flask_unchained.di.Service` and live in a bundle's ``services`` module. You can however manually register anything as a "service", even plain values if you really wanted to, using the ``unchained.service`` decorator and/or the ``unchained.register_service`` method:

.. code-block::

    from flask_unchained import unchained

    @unchained.service(name='something')
    class SomethingNotExtendingService:
        pass

    A_CONST = 'a constant'
    unchained.register_service('A_CONST', A_CONST)

Services can request other services be injected into them, and as long as there are no circular dependencies, it will work:

.. code-block::

    from flask_unchained import Service, injectable

    class OneService(Service):
        pass

    class TwoService(Service):
        one_service: OneService = injectable

By setting the default value of a class attribute or function/method argument to the :attr:`flask_unchained.injectable` constant, you are informing the :class:`~flask_unchained.Unchained` extension that it should inject those arguments.

.. admonition:: Important
    :class: info

    The names of services must be unique across *all* of the bundles in your app (by default services are named as the snake_cased class name). If there are any conflicting class names then you will need to use the ``unchained.service`` decorator or the ``unchained.register_service`` method to customize the name the service gets registered under::

       from flask_unchained import Service, unchained

       @unchained.service('a_unique_name')
       class ServiceWithNameConflict(Service):
           pass

Automatic Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dependency injection works automatically on all classes extending :class:`~flask_unchained.di.Service` and :class:`~flask_unchained.bundles.controller.controller.Controller`. The easiest way is with class attributes:

.. code-block::

    from flask_unchained import Controller, injectable
    from flask_unchained.bundles.security import Security, SecurityService
    from flask_unchained.bundles.sqlalchemy import SessionManager

    class SecurityController(Controller):
        security: Security = injectable
        security_service: SecurityService = injectable
        session_manager: SessionManager = injectable

Manual Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``unchained.inject`` decorator just about anywhere else you want to inject something::

   from flask_unchained import unchained, injectable

   # decorate a class to use class attributes injection
   @unchained.inject()
   class Foobar:
       some_service: SomeService = injectable

       # or you can decorate individual methods
       @unchained.inject()
       def a_method(self, another_service: AnotherService = injectable):
           pass

   # it works on regular functions too
   @unchained.inject()
   def a_function(some_service: SomeService = injectable):
       pass

Alternatively, you can also use ``unchained.get_local_proxy``:

.. code-block::

    from flask_unchained import unchained

    db = unchained.get_local_proxy('db')

Extending and Overriding Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Services are just classes, so they follow the normal Python inheritance rules, all you need to do is name your service the same as the one you want to customize, placed in the ``services`` module higher up in the bundle hierarchy (i.e. in a bundle extending another bundle, or in your app bundle).

Integrating Flask Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extensions that can be used in Flask Unchained bundles have a few limitations. The primary one being, the extension must implement ``init_app``, and its signature must take a single argument: ``app``. Some extensions fit this restriction out of the box, but often times you will need to subclass the extension to make sure its ``init_app`` signature matches. You can create new config options to replace arguments that were originally passed into the extension's constructor and/or ``init_app`` method.

In order for Flask Unchained to actually discover and initialize the extension you want to include, they must be placed in your bundle's ``extensions`` module. It looks like this:

.. code:: python

   # your_bundle/extensions.py

   from flask_whatever import WhateverExtension

   whatever = WhateverExtension()

   EXTENSIONS = {
       'whatever': whatever,
   }

The keys of the ``EXTENSIONS`` dictionary serve as the name that will be used to reference the extension at runtime (and for dependency injection). There can be multiple extensions per bundle, and you can also declare other extensions as dependencies that must be initialized before yours:

.. code:: python

   EXTENSIONS = {
       'whatever': (whatever, ['dep_ext_one', 'dep_ext_two']),
   }
