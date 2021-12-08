.. BEGIN setup/comments -------------------------------------------------------

   The heading hierarchy is defined as:
        h1: =
        h2: -
        h3: ^
        h4: ~
        h5: "
        h6: #

.. BEGIN document -------------------------------------------------------------

Flask Unchained
===============

Flask Unchained is a fully integrated, declarative, object-oriented web framework built with and for Flask and its extension ecosystem. It is a micro-framework, and simultaneously a full-stack framework with all the best batteries optionally included:

- SQLAlchemy ORM with Alembic Database Migrations
- GraphQL and/or Marshmallow RESTful APIs
- Authentication and Authorization
- Admin Interface
- Celery Distributed Tasks Queue
- pytest Testing Framework
- And more!

Flask Unchained aims to improve your development experience by using simple, consistent patterns so that everything works together out-of-the-box without boilerplate or plumbing, while also being highly extensible and completely customizable.

Install Flask Unchained
-----------------------

Requires **Python 3.7+**

.. code:: shell

    pip install "flask-unchained[dev]"

Hello World
---------------------

The iconic Hello World is as simple as it gets:

.. code-block::

    # project-root/app.py
    from flask_unchained import AppBundle, route

    class App(AppBundle):
        pass

    @route('/')
    def index():
        return 'Hello World from Flask Unchained!'

    def test_index(client):
        r = client.get('app.index')
        assert r.status_code == 200
        assert r.html == 'Hello World from Flask Unchained!'

Running the Development Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run your apps using ``flask run``:

.. code:: shell

    cd project-root
    flask run
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Testing with pytest
^^^^^^^^^^^^^^^^^^^

Tests are run using ``pytest``:

.. code:: shell

    cd project-root
    pytest app.py
    ============================= test session starts ==============================
    platform linux -- Python 3.8.6, pytest-6.1.2, py-1.9.0, pluggy-0.13.1
    rootdir: /home/user/dev/project-root
    plugins: flask-1.2.0, Flask-Unchained-0.9.1
    collected 1 item

    app.py .                                                                  [100%]

    ============================== 1 passed in 0.05s ===============================

Hello Batteries Included
------------------------

In only 80 or so lines of code, we have a fully-featured quotes app with an SQLAlchemy database, an HTML frontend, a RESTful JSON API with Marshmallow serialization and Swagger documentation, and a secured Admin interface for managing the database. This app also previews some of the new features Flask Unchained brings to the table over Flask and Django including dependency injection and declarative routing.

We require some extra dependencies to run this example, which are installed by adding the bundle names to the package requirements:

.. code:: shell

    pip install "flask-unchained[dev,admin,api,session,security,sqlalchemy]"

.. code-block::

    # project-root/app.py
    from flask_unchained import AppBundle, BundleConfig, FlaskUnchained, unchained, injectable
    from flask_unchained.views import Controller, route
    from flask_unchained.routes import controller, resource, include, prefix
    from flask_unchained.bundles.admin import ModelAdmin
    from flask_unchained.bundles.api import api, ma, OpenAPIController
    from flask_unchained.bundles.sqlalchemy import db

    BUNDLES = [
        'flask_unchained.bundles.admin',       # Flask-Admin
        'flask_unchained.bundles.api',         # RESTful APIs w/ Flask-Marshmallow
        'flask_unchained.bundles.babel',       # Flask-BabelEx
        'flask_unchained.bundles.session',     # Flask-Session
        'flask_unchained.bundles.security',    # Flask-Security
        'flask_unchained.bundles.sqlalchemy',  # SQLAlchemy-Unchained and Flask-Migrate
    ]

    class Config(BundleConfig):
        SECRET_KEY = 'super-sekret'
        WTF_CSRF_ENABLED = True
        SESSION_TYPE = 'sqlalchemy'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # :memory:

    class Quote(db.Model):
        class Meta:
            repr = ('id', 'quote', 'author')
            unique_together = ('quote', 'author')

        quote = db.Column(db.Text)
        author = db.Column(db.String)

    class QuoteManager(db.ModelManager):
        class Meta:
            model = Quote

    class QuoteSerializer(ma.ModelSerializer):
        class Meta:
            model = Quote

    class QuoteResource(api.ModelResource):
        class Meta:
            model = Quote

    class SiteController(Controller):
        quote_manager: QuoteManager = injectable

        @route('/')
        def index(self):
            return self.render_template_string(
                """
                <h1>Quotes</h1>
                {% for quote in quotes %}
                  <blockquote>
                    {{ quote.quote }}
                    <figcaption>
                      <cite>- {{ quote.author }}</cite>
                    </figcaption>
                  </blockquote>
                {% endfor %}
                """,
                quotes=self.quote_manager.all(),
            )

    class QuoteAdmin(ModelAdmin):
        model = Quote

    class App(AppBundle):
        def before_init_app(self, app: FlaskUnchained):
            app.url_map.strict_slashes = False

        @unchained.inject()
        def after_init_app(self, app: FlaskUnchained, quote_manager: QuoteManager = injectable):
            db.create_all()
            joys_soul, _ = quote_manager.get_or_create(
                quote='Things won are done, joys soul lies in the doing.',
                author='Shakespeare',
                commit=True,
            )

    routes = lambda: [
        controller(SiteController),
        prefix('/api/v1', [
            resource('/quotes', QuoteResource),
            controller('/docs', OpenAPIController),
        ]),
        include('flask_unchained.bundles.admin.routes'),
    ]

The app is run just as before with ``flask run``. Below, we list the URLs for the app resulting from the use of Flask Unchained's declarative routing:

.. code-block::

    flask urls
    Method(s)  Rule                      Endpoint                    View
    -------------------------------------------------------------------------------------------------------------------------------------------------------------
          GET  /                         site_controller.index       app.SiteController.index
          GET  /api/v1/quotes            quote_resource.list         app.QuoteResource.list
         POST  /api/v1/quotes            quote_resource.create       app.QuoteResource.create
          GET  /api/v1/quotes/<int:id>   quote_resource.get          app.QuoteResource.get
        PATCH  /api/v1/quotes/<int:id>   quote_resource.patch        app.QuoteResource.patch
          PUT  /api/v1/quotes/<int:id>   quote_resource.put          app.QuoteResource.put
       DELETE  /api/v1/quotes/<int:id>   quote_resource.delete       app.QuoteResource.delete
          GET  /admin                    admin.index                 flask_unchained.bundles.admin.views.dashboard.index
    GET, POST  /admin/login              admin.login                 flask_unchained.bundles.admin.views.admin_security_controller.AdminSecurityController.login
          GET  /admin/logout             admin.logout                flask_unchained.bundles.admin.views.admin_security_controller.AdminSecurityController.logout

.. admonition:: Thanks and acknowledgements
    :class: tip

    The architecture of how Flask Unchained works is only possible thanks to Python 3. The concepts and design patterns Flask Unchained introduces are inspired by the `Symfony Framework <https://symfony.com>`_, which is awesome, aside from the fact that it isn't Python ;)

    For those already familiar with `Flask <https://flask.palletsprojects.com/en/2.0.x/>`_, Flask Unchained stays true to the spirit and API of Flask and its extensions. Flask Unchained stands on the shoulders of giants, utilizing many existing Flask extensions and offering you complete flexibility to integrate your own. Indeed, Flask Unchained can even run atop `Quart <https://pgjones.gitlab.io/quart/>`_ for applications requiring deep asyncio integration (experimental!).

.. admonition:: Attention
    :class: warning

    This software is somewhere between alpha and beta quality. The design patterns are proven and the core is solid, but especially at the edges bugs are likely. There may also be some breaking API changes. Flask Unchained needs you: if you encounter any problems, have any questions, or have any feedback `please file issues on GitHub <https://github.com/briancappello/flask-unchained/issues>`_ !

Going Big (Project Layout)
--------------------------

When you want to expand beyond a single file, Flask Unchained defines a standardized (but configurable) folder structure for you - known as a "bundle" - so that everything continues to *just work*. A typical structure looks like this:

.. code-block:: shell

    /home/user/dev/project-root
    ├── app                 # the app bundle Python package
    │   ├── admins          # Flask-Admin model admins
    │   ├── commands        # Click CLI groups/commands
    │   ├── extensions      # Flask extensions
    │   ├── models          # SQLAlchemy models
    │   ├── fixtures        # SQLAlchemy model fixtures (for seeding the dev db)
    │   ├── serializers     # Marshmallow serializers (aka schemas)
    │   ├── services        # dependency-injectable Services
    │   ├── tasks           # Celery tasks
    │   ├── templates       # Jinja2 templates
    │   ├── views           # Controllers, Resources and ModelResources
    │   ├── __init__.py     # your AppBundle subclass
    │   ├── config.py       # your app config
    │   └── routes.py       # declarative routes
    ├── bundles             # custom bundles and/or bundle extensions/overrides
    │   └── security        # a customized/extended Security Bundle
    │       ├── models
    │       ├── serializers
    │       ├── services
    │       ├── templates
    │       └── __init__.py
    ├── db
    │   └── migrations      # migrations generated by Flask-Migrate
    ├── static              # the top-level static assets folder
    ├── templates           # the top-level templates folder
    └── tests               # your pytest tests

Continue reading to dive deeper into many of the features Flask Unchained brings to the table, or check out the :ref:`tutorial` to start building now! There are also some example open source apps available:

* `Flask React SPA <https://github.com/briancappello/flask-unchained-react-spa>`_
* `Flask Techan Unchained <https://github.com/briancappello/flask-techan-unchained>`_
* Open a PR to `add yours <https://github.com/briancappello/flask-unchained/pulls>`_!

Feature Overview
----------------

Bundles
^^^^^^^

Bundles are powerful and flexible. They are standalone Python packages that can do anything from integrate Flask extensions to be full-blown apps your app can integrate and extend (like, say, a blog or web store). Conceptually, a bundle *is* a blueprint, and Flask Unchained gives you complete control to configure not only which views from each bundle get registered with your app and at what routes, but also to extend and/or override anything else you might want to from the bundles you enable.

Some examples of what you can customize from 3rd-party bundles include configuration, controllers, resources, and routes, templates, extensions and services, and models and serializers. Each uses simple and consistent patterns that work the same way across every bundle. Extended/customized bundles can themselves also be distributed as their own projects, and support the same patterns for customization, ad infinitum.

Bundle Structure
~~~~~~~~~~~~~~~~

The example "Hello World" app bundles lived in a single file, while a "full" bundle package typically consists of many modules (as shown just above under Project Layout). The module locations for your code are customizable on a per-bundle basis by setting class attributes on your :class:`~flask_unchained.Bundle` subclass, for example:

.. code-block::

    # your_custom_bundle/__init__.py

    from flask_unchained import Bundle

    class YourCustomBundle(Bundle):
        config_module_name = 'settings'
        routes_module_name = 'urls'
        views_module_names = ['controllers', 'resources', 'views']

You can see the default module names and the override attribute names to set on your :class:`~flask_unchained.Bundle` subclass by printing the ordered list of hooks that will run for your app using ``flask unchained hooks``:

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

The API here is the same as :class:`flask.Blueprint`, however, its methods must be accessed via the :class:`~flask_unchained.Unchained` extension. The syntax is ``@unchained.bundle_name.blueprint_method_name``.

.. admonition:: Wait but why?
    :class: warning

    Sadly, there are some very serious technical limitations with the implementation of :class:`flask.Blueprint` such that its direct usage breaks the power and flexibility of Flask Unchained. Under the hood, Flask Unchained does indeed use a blueprint for each bundle - you just never interact with them directly.

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

When defining the app bundle, you must subclass :class:`~flask_unchained.AppBundle` instead of :class:`~flask_unchained.Bundle`:

.. code-block::

    # project-root/app/__init__.py

    from flask_unchained import AppBundle

    class App(AppBundle):
        pass

Everything about your app bundle is otherwise the same as regular bundles, except **the app bundle can extend and/or override anything from any bundle**.

The App Factory
^^^^^^^^^^^^^^^

The :class:`~flask_unchained.AppFactory` discovers all the code from your app and its bundles, and then with it automatically initializes, configures, and "boots up" the Flask ``app`` instance for you. I realize that probably sounds like black magic, but it's actually quite easy to understand, and every step it takes can be customized by you if necessary. The ``flask`` and ``pytest`` CLI commands automatically use the app factory for you, while in production you have to call it yourself:

.. code-block::

    # project-root/wsgi.py
    from flask_unchained import AppFactory, PROD

    app = AppFactory().create_app(env=PROD)

For a deeper look under the covers check out :doc:`how-flask-unchained-works`.

The Unchained Extension
^^^^^^^^^^^^^^^^^^^^^^^

The "orchestrator" that ties everything together. It handles dependency injection and enables access to much of the public API of ``flask.Flask`` and ``flask.Blueprint``:

.. code-block::

    # project-root/app.py
    from flask_unchained import unchained, injectable

    @unchained.inject()
    def print_hello(name: str, hello_service: HelloService = injectable):
        print(hello_service.hello_world(name))

    @unchained.before_first_request
    def runs_once_at_startup():
        print_hello("App")

    @unchained.app.after_request
    def runs_after_each_request_to_an_app_bundle_view(response):
        print_hello("Response")
        return response

Controllers, Resources, and Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Controller Bundle includes two base classes that all of your views should extend. The first is :class:`~flask_unchained.Controller`, and the second is :class:`~flask_unchained.Resource`, meant for building RESTful APIs.

Controller
~~~~~~~~~~

Chances are :class:`~flask_unchained.Controller` is the base class you want to extend, unless you're building a RESTful API. Controllers support multiple routes include a bit of default (customizable) magic:

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
            return self.render('site/foo_baz.html')  # template paths can be explicit

        # defaults to @route('/view-one', methods=['GET'])
        def view_one():
            # or just the filename
            return self.render('one')  # equivalent to 'site/one.html'

        # defaults to @route('/view-two', methods=['GET'])
        def view_two():
            return self.render('two')

        # utility function (gets no route)
        def _protected_function():
            return 'not a view'

On any subclass of :class:`~flask_unchained.Controller` that isn't abstract, all public methods are automatically assigned default routing rules. In the example above, ``foo_baz`` has a route decorator, but ``view_one`` and ``view_two`` do not. The undecorated views will be assigned default routing rules of ``/view-one`` and ``/view-two`` respectively (the default is to convert the method name to kebab-case). Protected methods (those prefixed with ``_``) are not assigned routes.

Templates
~~~~~~~~~

Flask Unchained uses the `Jinja <https://jinja.palletsprojects.com/en/2.10.x/templates/>`_ templating language, just like Flask.

By default bundles are configured to use a ``templates`` subfolder. This is customizable per-bundle:

.. code-block::

    # your_bundle/__init__.py

    from flask_unchained import Bundle

    class YourBundle(Bundle):
        template_folder = 'templates'  # the default

Controller classes each have their own template folder within :attr:`Bundle.template_folder`. It defaults to the snake_cased class name, with the suffixes ``Controller`` or ``View`` stripped (if any). You can customize it using :attr:`Controller.Meta.template_folder`.

The default file extension used for templates is configured by setting ``TEMPLATE_FILE_EXTENSION`` in your app config. It defaults to ``.html``, and is also configurable on a per-controller basis by setting :attr:`Controller.Meta.template_file_extension`.

Therefore, the above controller corresponds to the following templates folder structure:

.. code-block:: shell

   ./your_bundle
   ├── templates
   │   └── site
   │       ├── foo_baz.html
   │       ├── one.html
   │       └── two.html
   ├── __init__.py
   └── views.py

Extending and Overriding Templates
""""""""""""""""""""""""""""""""""

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~flask_unchained.Resource` class extends :class:`~flask_unchained.Controller` to add support for building RESTful APIs. The implementation draws much inspiration from `Flask-RSETful <https://flask-restful.readthedocs.io/en/latest/>`_ (specifically, the `Resource <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L543>`_ and `Api <https://github.com/flask-restful/flask-restful/blob/f9790d2be816b66b3cb879783de34e7fbe8b7ec9/flask_restful/__init__.py#L38>`_ classes). Using :class:`~flask_unchained.Resource` adds a bit more magic to controllers around specific methods:

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
          GET  /                        site_controller.index       app.views.SiteController.index
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
          GET  /                                     site_controller.index                 app.views.SiteController.index
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

Dependency Injection and Services
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Flask Unchained supports dependency injection of services and extensions (by default).

Services
~~~~~~~~

For services to be automatically discovered, they must subclass :class:`~flask_unchained.di.Service` and (by default) live in a bundle's ``services`` or ``managers`` modules. You can however manually register anything as a "service", even plain values if you really wanted to, using the ``unchained.service`` decorator and/or the ``unchained.register_service`` method:

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
        something: SomethingNotExtendingService = injectable
        A_CONST: str = injectable

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

It also works on the constructor, which is functionally equivalent, just more verbose:

.. code-block::

    class SiteController(Controller):
        def __init__(self, security: Security = injectable):
            self.security = security

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

Services are just classes, so they follow the normal Python inheritance rules. All you need to do is name your service the same as the one you want to customize, placed in the ``services`` module higher up in the bundle hierarchy (i.e. in a bundle extending another bundle, or in your app bundle).

Integrating Flask Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Flask Unchained is designed to work with the existing Flask extensions ecosystem. That said, there will often be a few customizations required to make them work with Flask Unchained. The primary one being, the extension must implement ``init_app``, and its signature must take a single argument: ``app``. Some extensions fit this restriction out of the box, but often times you will need to subclass the extension to make sure its ``init_app`` signature matches. You can create new config options to replace arguments that were originally passed into the extension's constructor and/or ``init_app`` method.

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
