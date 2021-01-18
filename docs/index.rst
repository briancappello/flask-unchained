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

**The quickest and easiest way to build large web apps and APIs with Flask and SQLAlchemy**

Flask Unchained is a fully integrated, declarative, object-oriented web framework for Flask and its optional-batteries-included extension ecosystem. Flask Unchained is powerful, consistent, highly extensible and completely customizable. Flask Unchained stays true to the spirit and API of Flask while simultaneously introducing powerful new building blocks that enable you to rapidly take your Flask apps to the next level:

- clean and predictable application structure that encourage good design patterns by organizing code as bundles
- no integration headaches between supported libraries and extensions
- no plumbing or boilerplate; everything just works straight out-of-the-box
- simple and consistent patterns for customizing and/or overriding *everything*
- designed with code reuse in mind; your bundles can be distributed as their own Python packages to automatically integrate with other Flask Unchained apps

.. admonition:: Included bundles & integrated extensions (mostly optional)
    :class: tip

    - **Controller Bundle**: Enhanced class-based views, enhanced blueprints, declarative routing, and `Flask WTF <https://flask-wtf.readthedocs.io/en/stable/>`_ for forms and CSRF protection. The only required bundle.
    - **SQLAlchemy Bundle** `Flask SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>`_ and `Flask Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_ for database models and migrations, plus some optional "sugar" on top of `SQLAlchemy <https://www.sqlalchemy.org/>`_ to make the best ORM in existence even quicker and easier to use with `SQLAlchemy Unchained <https://sqlalchemy-unchained.readthedocs.io/en/latest/>`_.
    - **API Bundle**: RESTful APIs with `Flask Marshmallow <https://flask-marshmallow.readthedocs.io/en/latest/>`_ serializers for SQLAlchemy models.
    - **Graphene Bundle**: `Flask GraphQL <https://github.com/graphql-python/flask-graphql>`_ with `Graphene <https://docs.graphene-python.org/en/latest/quickstart/>`_ for SQLAlchemy models.
    - **Security Bundle**: `Flask Login <https://flask-login.readthedocs.io/en/latest/>`_ for authentication and `Flask Principal <https://pythonhosted.org/Flask-Principal/>`_ for authorization.
    - **Celery Bundle**: `Celery <http://www.celeryproject.org/>`_ distributed tasks queue.
    - `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_, `Flask BabelEx <https://pythonhosted.org/Flask-BabelEx/>`_, `Flask Mail <https://pythonhosted.org/Flask-Mail/>`_, `Flask Session <https://flask-session.readthedocs.io/en/latest/>`_, ...
    - Don't like the default stack? With Flask Unchained you can bring your own! Flask Unchained is designed to be so flexible that you could even use it to create your own works-out-of-the-box web framework for Flask with an entirely different stack.

.. admonition:: Thanks and acknowledgements
    :class: tip

    The architecture of how Flask Unchained and its bundles works is only possible thanks to Python 3. The concepts and design patterns Flask Unchained introduces are inspired by the `Symfony Framework <https://symfony.com>`_, which is enterprise-proven and awesome, aside from the fact that it isn't Python ;)

Install Flask Unchained
-----------------------

Requires **Python 3.6+**

.. code:: shell

    pip install "flask-unchained[dev]"

Or, to use **asyncio** by running atop `Quart <https://pgjones.gitlab.io/quart/>`_ instead of Flask **(experimental!)**:

.. code:: shell

    pip install "flask-unchained[asyncio,dev]"  # Requires Python 3.7+

.. admonition:: Attention
    :class: warning

    This software is somewhere between alpha and beta quality. It works for me, the design patterns are proven and the core is solid, but especially at the edges there will probably be bugs - and possibly some breaking API changes too. Flask Unchained needs you: `please file issues on GitHub <https://github.com/briancappello/flask-unchained/issues>`_ if you encounter any problems, have any questions, or have any feedback!

Hello World
-----------

As simple as it gets:

.. code-block::

    # project-root/app.py
    from flask_unchained import AppBundle, Controller route

    class App(AppBundle):
        pass

    class SiteController(Controller):
        @route('/')
        def index(self):
            return 'Hello World from Flask Unchained!'

Running the Development Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

And just like that we can run it:

.. code:: shell

    cd project-root
    UNCHAINED="app" flask run
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

You can now browse to `http://127.0.0.1:5000 <http://127.0.0.1:5000>`_ to see it in action!

Under the easily accessible hood lives Flask Unchained's fully customizable App Factory: the good old call to ``app = Flask(__name__)`` and everything else necessary to correctly initialize, register, and run your app's code. **No plumbing, no boilerplate, everything just works.**

Testing with pytest
^^^^^^^^^^^^^^^^^^^

Python's best testing framework comes integrated out-of-the-box:

.. code-block::

    # project-root/test_app.py
    from flask_unchained.pytest import HtmlTestClient

    class TestSiteController:
        def test_index(self, client: HtmlTestClient):
            r = client.get('site_controller.index')
            assert r.status_code == 200
            assert r.html.count('Hello World from Flask Unchained!') == 1

Tests can be run like so:

.. code:: shell

    cd project-root
    UNCHAINED="app" pytest
    ============================= test session starts ==============================
    platform linux -- Python 3.8.6, pytest-6.1.2, py-1.9.0, pluggy-0.13.1
    rootdir: /home/user/dev/project-root
    plugins: Faker-4.1.1, flask-1.1.0, Flask-Unchained-0.7.9
    collected 1 item

    test_app.py .                                                            [100%]

    ============================== 1 passed in 0.05s ===============================

The Production App Factory
^^^^^^^^^^^^^^^^^^^^^^^^^^

In development and testing the app factory is automatically used, while in production you call it yourself:

.. code-block::

    # project-root/wsgi.py
    from flask_unchained import AppFactory, PROD

    app = AppFactory().create_app(env=PROD)

We've just shown how Flask Unchained keeps the minimal simplicity micro-frameworks like Flask are renowned for, but to really begin to grasp the power of using Flask Unchained, we need to go bigger than this simple example!

Hello World for Real
--------------------

Let's take a peak at some of what this baby can really do to see just how quickly you can start building something more useful:

.. code:: shell

    cd project-root
    mkdir -p templates/site
    pip install "flask-unchained[dev,sqlalchemy]"

Quotes App
^^^^^^^^^^

We're going to create a simple app to store authors and quotes in an SQLite database, and to display them to the user in their browser.

.. code-block::

    # project-root/app.py
    from flask_unchained import (FlaskUnchained, AppBundle, BundleConfig,
                                 unchained, injectable, generate_csrf)
    from flask_unchained.views import Controller, route, param_converter
    from flask_unchained.bundles.sqlalchemy import db, ModelManager

    # configuration ---------------------------------------------------------------------
    BUNDLES = ['flask_unchained.bundles.sqlalchemy']

    class Config(BundleConfig):
        SECRET_KEY = 'super-secret-key'
        WTF_CSRF_ENABLED = True
        SQLALCHEMY_DATABASE_URI = 'sqlite://'  # memory

    class TestConfig(Config):
        WTF_CSRF_ENABLED = False

    @unchained.after_request
    def set_csrf_token_cookie(response):
        if response:
            response.set_cookie('csrf_token', generate_csrf())
        return response


    # database models -------------------------------------------------------------------
    class Author(db.Model):
        # models get a primary key (id) and created_at/updated_at columns by default
        name = db.Column(db.String(length=64))
        quotes = db.relationship('Quote', back_populates='author')

    class Quote(db.Model):
        text = db.Column(db.Text)
        author = db.relationship('Author', back_populates='quotes')
        author_id = db.foreign_key('Author', nullable=False)


    # model managers (dependency-injectable services for database CRUD operations) ------
    class AuthorManager(ModelManager):
        class Meta:
            model = Author

    class QuoteManager(ModelManager):
        class Meta:
            model = Quote


    # views (controllers) ---------------------------------------------------------------
    class SiteController(Controller):
        class Meta:
            template_folder = 'site'  # the default, auto-determined from class name

        # get the app's instance of the QuoteManager service injected into us
        quote_manager: QuoteManager = injectable

        @route('/')
        def index(self):
            return self.render('index', quotes=self.quote_manager.all())

        @route('/authors/<int:id>')
        @param_converter(id=Author)  # use `id` in the URL to query that Author in the DB
        def author(self, author: Author):
            return self.render('author', author=author)


    # declare this module (file) is a Flask Unchained Bundle by subclassing AppBundle ---
    class App(AppBundle):
        def before_init_app(self, app: FlaskUnchained) -> None:
            app.url_map.strict_slashes = False

        @unchained.inject()
        def after_init_app(self,
                           app: FlaskUnchained,
                           author_manager: AuthorManager = injectable,
                           quote_manager: QuoteManager = injectable,
                           ) -> None:
            # typically you should use DB migrations and fixtures to perform these steps
            db.create_all()
            quote_manager.create(
                text="Happiness is not a station you arrive at, "
                     "but rather a manner of traveling.",
                author=author_manager.create(name="Margaret Lee Runbeck"))
            quote_manager.create(
                text="Things won are done; joy's soul lies in the doing.",
                author=author_manager.create(name="Shakespeare"))
            db.session.commit()

That's the complete app code right there! Hopefully this helps show what is meant by Flask Unchained minimizing plumbing and boilerplate by being *declarative* and *object-oriented*. We just need to add the template files before starting the server:

.. code:: html+jinja

    <!-- project-root/templates/layout.html -->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Flask Unchained Quotes</title>
    </head>
    <body>
        <nav>
            <a href="{{ url_for('site_controller.index') }}">Home</a>
        </nav>
        {% block body %}
        {% endblock %}
    </body>
    </html>

.. code:: html+jinja

    <!-- project-root/templates/site/index.html -->
    {% extends "layout.html" %}

    {% block body %}
        <h1>Flask Unchained Quotes</h1>
        {% for quote in quotes %}
            <blockquote>
                {{ quote.text }}<br />
                <a href="{{ url_for('site_controller.author', id=quote.author.id) }}">
                    {{ quote.author.name }}
                </a>
            </blockquote>
        {% endfor %}
    {% endblock %}

.. code:: html+jinja

    <!-- project-root/templates/site/author.html -->
    {% extends "layout.html" %}

    {% block body %}
        <h1>{{ author.name }} Quotes</h1>
        {% for quote in author.quotes %}
            <blockquote>{{ quote.text }}</blockquote>
        {% endfor %}
    {% endblock %}

Fire it up:

.. code:: shell

    export UNCHAINED="app"
    flask urls
    Method(s)  Rule                         Endpoint                View
    -------------------------------------------------------------------------------------------
          GET  /                            site_controller.index   app.SiteController.index
          GET  /authors/<int:id>            site_controller.author  app.SiteController.author

.. code:: shell

    export UNCHAINED="app"
    flask run
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Adding a RESTful API
^^^^^^^^^^^^^^^^^^^^

Flask Unchained includes an API Bundle integrating RESTful support atop the Controller Bundle with SQLAlchemy models and Marshmallow serializers. Basic out-of-the-box usage is dead simple.

Install dependencies for the API Bundle:

.. code:: shell

    pip install "flask-unchained[api]"

And add the following code to the bottom of ``project-root/app.py``:

.. code-block::

    # append to project-root/app.py
    from flask_unchained.bundles.api import ma, ModelResource, ModelSerializer
    from flask_unchained.routes import controller, resource, prefix

    BUNDLES += ['flask_unchained.bundles.api']

    # db model serializers --------------------------------------------------------------
    class AuthorSerializer(ModelSerializer):
        class Meta:
            model = Author
            url_prefix = '/authors'  # the default, auto-determined from model class name

        quotes = ma.Nested('QuoteSerializer', only=('id', 'text'), many=True)

    class QuoteSerializer(ModelSerializer):
        class Meta:
            model = Quote

        author = ma.Nested('AuthorSerializer', only=('id', 'name'))

    # api views -------------------------------------------------------------------------
    class AuthorResource(ModelResource):
        class Meta:
            model = Author
            include_methods = ('get', 'list')

    class QuoteResource(ModelResource):
        class Meta:
            model = Quote
            exclude_methods = ('create', 'patch', 'put', 'delete')

    # use declarative routing for specifying views with fine-grained control over URLs
    routes = lambda: [
        controller(SiteController),
        prefix('/api/v1', [
            resource(AuthorResource),
            resource(QuoteResource),
        ]),
    ]

We can take a look at the new URLs:

.. code:: shell

    flask urls
    Method(s)  Rule                       Endpoint                View
    -------------------------------------------------------------------------------------------
          GET  /                          site_controller.index   app.SiteController.index
          GET  /authors/<int:id>          site_controller.author  app.SiteController.author
          GET  /api/v1/authors            author_resource.list    app.AuthorResource.list
          GET  /api/v1/authors/<int:id>   author_resource.get     app.AuthorResource.get
          GET  /api/v1/quotes             quote_resource.list     app.QuoteResource.list
          GET  /api/v1/quotes/<int:id>    quote_resource.get      app.QuoteResource.get

And run it:

.. code:: shell

    flask run
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Securing the App
^^^^^^^^^^^^^^^^

Flask Unchained also includes the Security Bundle as a foundation for handling authentication and authorization in your apps. It is designed to be extended and customized to your needs - like everything in Flask Unchained! - but it also works out-of-the-box for when all it provides is sufficient for your needs. Let's set things up to require an authenticated user to use the app's API.

Install dependencies for the Security Bundle:

.. code:: shell

    pip install "flask-unchained[session,security]"

And add the following to the bottom of your ``project-root/app.py``:

.. code-block::

    # append to project-root/app.py
    from flask_unchained.bundles.security import SecurityController, auth_required
    from flask_unchained.bundles.security import SecurityService, UserManager
    from flask_unchained.bundles.security.models import User as BaseUser
    from flask_unchained.bundles.sqlalchemy import db

    # enable the session and security bundles
    BUNDLES += ['flask_unchained.bundles.session',
                'flask_unchained.bundles.security']

    # configure server-side sessions
    Config.SESSION_TYPE = 'sqlalchemy'
    Config.SESSION_SQLALCHEMY_TABLE = 'flask_sessions'

    # configure security
    Config.SECURITY_REGISTERABLE = True  # enable user registration
    AuthorResource.Meta.decorators = (auth_required,)
    QuoteResource.Meta.decorators = (auth_required,)

    # want to add fields to the database model for users? no problem!
    # just subclass it, keeping the same original class name
    class User(BaseUser):
        favorite_color = db.Column(db.String)

    # add the Security Controller views to our app
    routes = lambda: [
        controller(SiteController),
        controller(SecurityController),
        prefix('/api/v1', [
            resource('/authors', AuthorResource),
            resource('/quotes', QuoteResource),
        ]),
    ]

    # create a demo user and log them in when the dev server starts
    @unchained.before_first_request()
    @unchained.inject()
    def create_and_login_demo_user(user_manager: UserManager = injectable,
                                   security_service: SecurityService = injectable):
        user = user_manager.create(email='demo@example.com',
                                   password='password',
                                   favorite_color='magenta',
                                   is_active=True,
                                   commit=True)
        security_service.login_user(user)

By default the Security Bundle only comes with the ``/login`` and ``/logout`` URLs enabled. Let's confirm we've also enabled ``/register``:

.. code:: shell

    flask urls
    Method(s)  Rule                         Endpoint                      View
    -------------------------------------------------------------------------------------------------------------------------------
          GET  /                         site_controller.index         quotes.SiteController.index
          GET  /authors/<int:id>         site_controller.author        quotes.SiteController.author
          GET  /api/v1/authors           author_resource.list          quotes.AuthorResource.list
          GET  /api/v1/authors/<int:id>  author_resource.get           quotes.AuthorResource.get
          GET  /api/v1/quotes            quote_resource.list           quotes.QuoteResource.list
          GET  /api/v1/quotes/<int:id>   quote_resource.get            quotes.QuoteResource.get
    GET, POST  /login                    security_controller.login     flask_unchained.bundles.security.SecurityController.login
          GET  /logout                   security_controller.logout    flask_unchained.bundles.security.SecurityController.logout
    GET, POST  /register                 security_controller.register  flask_unchained.bundles.security.SecurityController.register

.. code:: shell

    flask run
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

NOTE: you'll need to logout the demo user by visiting `http://127.0.0.1:5000/logout <http://127.0.0.1:5000/logout>`_ before the login and register endpoints will work.

Going Big (Project Layout)
--------------------------

When you want to expand beyond a single file, Flask Unchained defines a standardized (but configurable) folder structure for you so that everything just works. A typical structure looks like this:

.. code-block:: shell

    /home/user/dev/project-root
    ├── unchained_config.py # the Flask Unchained config
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

Want to start building now? Check out the :ref:`tutorial`! There are also some example open source apps available:

* `Flask React SPA <https://github.com/briancappello/flask-unchained-react-spa>`_
* `Flask Techan Unchained <https://github.com/briancappello/flask-techan-unchained>`_
* Open a PR to `add yours <https://github.com/briancappello/flask-unchained/pulls>`_!

Features
--------

Bundles
^^^^^^^

Bundles are powerful and flexible. They are standalone Python packages that can do anything from integrate Flask extensions to be full-blown apps your app can integrate and extend (like, say, a blog or web store). Conceptually, a bundle *is* a blueprint, and Flask Unchained gives you complete control to configure not only which views from each bundle get registered with your app and at what routes, but also to extend and/or override anything else you might want to from the bundles you enable.

Some examples of what you can customize from bundles include configuration, controllers, resources, and routes, templates, extensions and services, and models and serializers. Each uses simple and consistent patterns that work the same way across every bundle. Extended/customized bundles can themselves also be distributed as their own projects, and support the same patterns for customization, ad infinitum.

Bundle Structure
~~~~~~~~~~~~~~~~

The example "hello world" app bundle lived in a single file, while a "full" bundle package typically consists of many modules (as shown just above under Project Layout). The module locations for your code are customizable on a per-bundle basis by setting class attributes on your :class:`~flask_unchained.Bundle` subclass, for example:

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

The :class:`~flask_unchained.Unchained` extension also plays a role in the app factory:

The App Factory
^^^^^^^^^^^^^^^

The :class:`~flask_unchained.AppFactory` discovers all the code from your app and its bundles, and then with it automatically initializes, configures, and "boots up" the Flask ``app`` instance for you. I know that sounds like magic, but it's actually quite easy to understand, and every step it takes can be customized by you if necessary. In barely-pseudo-code, the app factory looks like this:

.. code-block::

    from flask import Flask
    from flask_unchained import DEV, PROD, STAGING, TEST

    class AppFactory:
        APP_CLASS = Flask

        def create_app(self, env: Union[DEV, PROD, STAGING, TEST]) -> Flask:
            # load the Unchained Config and configured bundles
            unchained_config = self.load_unchained_config(env)
            app_bundle, bundles = self.load_bundles(unchained_config.BUNDLES)

            # instantiate the Flask app instance
            app = self.APP_CLASS(app_bundle.name, **kwargs_from_unchained_config)

            # let bundles configure the app pre-initialization
            for bundle in bundles:
                bundle.before_init_app(app)

            # discover code from bundles and boot the app using hooks
            unchained.init_app(app, bundles)
                # the Unchained extension runs hooks in their correct order:
                # (there may be more hooks depending on which bundles you enable)
                RegisterExtensionsHook.run_hook(app, bundles)
                ConfigureAppHook.run_hook(app, bundles)
                InitExtensionsHook.run_hook(app, bundles)
                RegisterServicesHook.run_hook(app, bundles)
                RegisterCommandsHook.run_hook(app, bundles)
                RegisterRoutesHook.run_hook(app, bundles)
                RegisterBundleBlueprintsHook.run_hook(app, bundles)

            # let bundles configure the app post-initialization
            for bundle in bundles:
                bundle.after_init_app(app)

            # return the app instance ready to rock'n'roll
            return app

The ``flask`` and ``pytest`` CLI commands automatically use the app factory for you, while in production you have to call it yourself:

.. code-block::

    # project-root/wsgi.py
    from flask_unchained import AppFactory, PROD

    app = AppFactory().create_app(env=PROD)

For a deeper look check out :doc:`how-flask-unchained-works`.

Controllers, Resources, and Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The controller bundle includes two base classes that all of your views should extend. The first is :class:`~flask_unchained.Controller`, and the second is :class:`~flask_unchained.Resource`, meant for building RESTful APIs.

Controller
~~~~~~~~~~

Chances are :class:`~flask_unchained.Controller` is the base class you want to extend, unless you're building a RESTful API. Under the hood, the implementation is actually very similar to :class:`flask.views.View`, however, they're not compatible. Controllers include a bit of magic:

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
