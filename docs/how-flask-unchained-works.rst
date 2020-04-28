.. BEGIN setup/comments -------------------------------------------------------

   The heading hierarchy is defined as:
        h1: =
        h2: -
        h3: ^
        h4: ~
        h5: "
        h6: #

.. BEGIN document -------------------------------------------------------------

How Flask Unchained Works
=========================

The Application Factory
-----------------------

The app factory might sound like magic, but it's actually quite easy to understand, and every step it takes is customizable by you, if necessary. The just-barely pseudo code looks like this:

.. code-block::

    class AppFactory:
        def create_app(self, env):
            # first load the user's unchained config
            unchained_config = self.load_unchained_config(env)

            # next load configured bundles
            app_bundle, bundles = self.load_bundles(unchained_config.BUNDLES)

            # instantiate the Flask app instance
            app = Flask(app_bundle.name, **kwargs_from_unchained_config)

            # let bundles configure the app pre-initialization
            for bundle in bundles:
                bundle.before_init_app(app)

            # discover code from bundles and boot up the Flask app using hooks
            unchained.init_app(app, bundles)
                # the Unchained extensions runs hooks in their correct order:
                # (there may be more depending on which bundles you enable)
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

            # return the finalized app ready to rock'n'roll
            return app

.. admonition:: Advanced
    :class: info

    You can subclass :class:`flask_unchained.AppFactory` if you need to customize any of its behavior. If you want to take things a step further, Flask Unchained can even be used to create your own redistributable batteries-included web framework for Flask using whichever stack of Flask extensions and Python libraries you prefer.

The Unchained Config
--------------------

The first thing the app factory does is to load your "Unchained Config". The unchained config is used to declare which bundles should be loaded, as well as for passing any optional keyword arguments to the ``Flask`` constructor.

Dedicated Module Mode
^^^^^^^^^^^^^^^^^^^^^

The most common way to configure Flask Unchained apps is with a module named ``unchained_config`` in the project root:

.. code::  shell

    /home/user/project-root
    ├── unchained_config.py    # your Unchained Config
    └── app.py                 # your App Bundle

The Unchained Config itself doesn't actually contain a whole lot. The only required setting is the ``BUNDLES`` list:

.. code-block::

    # project-root/unchained_config.py

    import os

    # kwargs to pass to the Flask constructor (must be uppercase, all optional)
    ROOT_PATH = os.path.dirname(__file__)  # determined automatically by default
    STATIC_FOLDER = "static"               # determined automatically by default
    STATIC_URL_PATH = "/static"            # determined automatically by default
    STATIC_HOST = None                     # None by default
    TEMPLATE_FOLDER = "templates"          # determined automatically by default
    HOST_MATCHING = False                  # False by default
    SUBDOMAIN_MATCHING = False             # False by default

    # the ordered list of bundles to load for your app (in dot-module notation)
    BUNDLES = [
        'flask_unchained.bundles.babel',       # always enabled, optional to list here
        'flask_unchained.bundles.controller',  # always enabled, optional to list here
        'app',  # your app bundle *must* be last
    ]

When ``unchained_config.py`` exists in the ``project-root`` directory, exporting ``UNCHAINED_CONFIG`` is not required, and the app can be run like so:

.. code-block:: shell

    cd project-root
    flask run

Single-File App Mode
^^^^^^^^^^^^^^^^^^^^

For single-file apps, you can "double purpose" the ``app`` module as your Unchained Config. This is as simple as it gets:

.. code-block::

    # project-root/app.py

    from flask_unchained import AppBundle, Controller, route

    class App(AppBundle):
        pass

    class SiteController(Controller):
        @route('/')
        def index(self):
            return 'hello world'

It can be run like so:

.. code-block:: shell

    export UNCHAINED_CONFIG="app"  # the module where the unchained config resides
    flask run

In the above example, we're essentially telling the app factory, "just use the defaults with my app bundle". In single-file mode, the app bundle is automatically detected, so there aren't actually any Unchained Config settings in the above file. To set them looks as you would expect:

.. code-block::

    # project-root/app.py

    import os
    from flask_unchained import AppBundle, Controller, route

    # kwargs to pass to the Flask constructor (must be uppercase, all optional)
    ROOT_PATH = os.path.dirname(__file__)  # determined automatically by default
    STATIC_FOLDER = "static"               # determined automatically by default
    STATIC_URL_PATH = "/static"            # determined automatically by default
    STATIC_HOST = None                     # None by default
    TEMPLATE_FOLDER = "templates"          # determined automatically by default
    HOST_MATCHING = False                  # False by default
    SUBDOMAIN_MATCHING = False             # False by default

    # the ordered list of bundles to load for your app (in dot-module notation)
    BUNDLES = [
        'flask_unchained.bundles.babel',       # always enabled, optional to list here
        'flask_unchained.bundles.controller',  # always enabled, optional to list here
        'app',  # your app bundle *must* be last
    ]

    class App(AppBundle):
        pass

    class SiteController(Controller):
        @route('/')
        def index(self):
            return 'hello world'

And once again, just be sure to ``export UNCHAINED_CONFIG="app"``:

.. code-block:: shell

    export UNCHAINED_CONFIG="app"  # the module where the unchained config resides
    flask run

Bundle.before/after_init_app
----------------------------

The most obvious place you can hook into the app factory is with your :class:`~flask_unchained.bundles.Bundle` subclass, for example:

.. code-block::

    # project-root/app.py

    from flask import Flask
    from flask_unchained import AppBundle

    class App(AppBundle):
        def before_init_app(app: Flask):
            app.url_map.strict_slashes = False

        def after_init_app(app: Flask):
            @app.after_request
            def do_stuff(response):
                return response

Using the :class:`~flask_unchained.unchained.Unchained` extension is another way to plug into the app factory, so let's look at that next.

The Unchained Extension
-----------------------

As an alternative to using ``Bundle.before_init_app`` and ``Bundle.after_init_app``, the :class:`~flask_unchained.unchained.Unchained` extension also acts as a drop-in replacement for some of the public API of :class:`~flask.Flask`:

.. code-block::

    from flask_unchained import unchained

    @unchained.before_first_request
    def called_once_before_the_first_request():
        pass

    # the other familiar decorators are also available:
    @unchained.url_value_preprocessor
    @unchained.url_defaults
    @unchained.before_request
    @unchained.after_request
    @unchained.errorhandler
    @unchained.teardown_request
    @unchained.teardown_appcontext
    @unchained.context_processor
    @unchained.shell_context_processor
    @unchained.template_filter
    @unchained.template_global
    @unchained.template_tag
    @unchained.template_test

These decorators all work exactly the same as if you were using them from the ``app`` instance itself.

The ``Unchained`` extension first forwards these calls to the ``Flask`` instance itself, and then it calls ``RunHooksHook.run_hook(app, bundles)``. Hooks are where the real action of actually booting up the app happens.

App Factory Hooks
-----------------

App Factory Hooks are what make sure all of the code from your configured list of bundles gets discovered and registered correctly with both the Flask ``app`` instance and the Unchained extension.

.. admonition:: Important
    :class: tip

    Hooks are what define the patterns to load and customize everything in bundles. By default, to override something, you just place it in your bundle with the same name and in the same location (module) as whatever you want to override, or to extend something, do the same while also subclassing whatever you wish to extend. In other words, you just use standard object-oriented Python while following consistent naming conventions.

.. admonition:: Advanced
    :class: info

    While it shouldn't be necessary, you can even extend and/or override hooks themselves if you need to customize their behavior.

These are some of the hooks Flask Unchained includes:

:InitExtensionsHook: Discovers Flask extensions in bundles and initializes them with the app.

:RegisterServicesHook: Discovers services in bundles and registers them with the :class:`~flask_unchained.unchained.Unchained` extension. Both services and extensions are dependency-injectable at runtime into just about anything that can be wrapped with the :meth:`~flask_unchained.unchained.Unchained.inject` decorator.

:ConfigureAppHook: Discovers configuration options in bundles and registers them with the app.

:RegisterCommandsHook: Discovers CLI commands in bundles and registers them with the app.

Hooks are also loaded from bundles, for example the Controller Bundle includes these:

:RegisterRoutesHook: Discovers all views/routes in bundles and registers any "top-level" ones with the app.

:RegisterBundleBlueprintsHook: Registers the views/routes in bundles as blueprints with the app. Each bundle gets (conceptually, is) its own blueprint.

:RegisterBlueprintsHook: Discovers legacy Flask Blueprints and registers them with the app.

For our simple "hello world" app, most of these are no-ops, with the exception of the hook to register bundle blueprints. This is the essence of it:

.. code-block::

    # flask_unchained/bundles/controller/hooks/register_bundle_blueprints_hook.py

    from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained
    from flask_unchained.bundles.controller.bundle_blueprint import BundleBlueprint

    class RegisterBundleBlueprintsHook(AppFactoryHook):
        def run_hook(self,
                     app: FlaskUnchained,
                     bundles: List[Bundle],
                     unchained_config: Optional[Dict[str, Any]] = None,
                     ) -> None:
            for bundle in bundles:
                bp = BundleBlueprint(bundle)
                for route in bundle.routes:
                    bp.add_url_rule(route.full_rule,
                                    defaults=route.defaults,
                                    endpoint=route.endpoint,
                                    methods=route.methods,
                                    **route.rule_options)
                app.register_blueprint(bp)

And the result can be seen by running ``flask urls``:

.. code-block:: shell

    flask urls
    Method(s)  Rule                     Endpoint                    View
    ----------------------------------------------------------------------------------------------
          GET  /static/<path:filename>  static                      flask.helpers.send_static_file
          GET  /                        site_controller.index       app.SiteController.index
          GET  /hello                   site_controller.hello       app.SiteController.hello

The Bundle Hierarchy
--------------------

FIXME: Expand on the bundle hierarchy and inheritance concept! Show examples.
