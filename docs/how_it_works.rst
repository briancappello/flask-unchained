How it Works
============

The App Factory
---------------

Flask Unchained implements the application factory pattern. There is one entry point,
:meth:`flask_unchained.AppFactory.create_app`:

.. code:: python

   # project-root/wsgi.py

   import os

   from flask_unchained import AppFactory, PROD


   app = AppFactory.create_app(os.getenv('FLASK_ENV', PROD))

(In development and testing, this happens automatically behind the scenes when you call
the ``flask`` or ``pytest`` commands.)

The :meth:`~flask_unchained.AppFactory.create_app` class method does the following:

1. It load's your project's ``unchained_config`` module.

2. It initializes all of the ``Bundle`` subclasses from those listed in ``unchained_config.BUNDLES``.

3. It initializes a ``FlaskUnchained`` app instance (which is just a minimally extended :class:`~flask.Flask` subclass).

4. For each bundle, it calls ``bundle.before_init_app(app)``.

5. It then finishes initializing the :class:`~flask_unchained.Unchained` extension, by calling ``unchained.init_app(app, env, bundles)``.

   * The ``Unchained`` extension will then register itself with the app, and it calls ``RunHooksHook.run_hook(app, bundles)``.
   * Hooks are subclasses of ``AppFactoryHook``, and the ``RunHooksHook`` will discover them in both core Flask Unchained as well as from the ``hooks`` module of each bundle in ``unchained_config.BUNDLES``. Hooks are responsible for the majority of the hard work required to initialize the application. They do things like loading configuration from all the bundles, initializing extensions, discovering models, and registering views and routes with Flask - to name some examples.

6. Afterwards, for each bundle, the app factory calls ``bundle.after_init_app(app)``.

7. Lastly, it returns the application instance, ready to rock and roll.

Hooks and Bundle Structure
--------------------------

Generally speaking, hooks are responsible for importing and discovering code, and then typically somehow registering those things with the app. They run in a specific order, determined dynamically from each hook's listed dependencies. Each hook can define an attribute, ``bundle_module_name``, that determines the module name in bundles that the hook will load from. Flask Unchained provides a command to make it easier to discover hooks and where they load from:

.. code:: bash

   $ flask unchained hooks
   Hook Name                    Default Bundle Module  Bundle Module Override Attr  Description
   ----------------------------------------------------------------------------------------------------------------------------------------------
   run_hooks_hook               hooks                  hooks_module_name            An internal hook to discover and run all the other hooks.
   extensions                   extensions             extensions_module_name       Registers extensions found in bundles with the current app.
   configure_app                config                 config_module_name           Updates app.config with the default settings of each bundle.
   init_extensions              extensions             extensions_module_name       Initializes extensions found in bundles with the current app.
   services                     services               services_module_name         Registers services for dependency injection.
   extension_services           (None)                 (None)                       Injects services into extensions.
   commands                     commands               commands_module_name         Adds commands and command groups from bundles.
   routes                       routes                 routes_module_name           Registers routes.
   bundle_blueprints            (None)                 (None)                       Registers a blueprint with each bundle's routes and template folder.
   blueprints                   views                  views_module_name            Registers blueprints.

We're interested in the ``Default Bundle Module`` and ``Bundle Module Override Attr`` columns. The first one defines where a hook will look in each bundle, by default. However, any bundle can override the setting for itself by defining the override attribute on itself, eg:

.. code:: python

   # your_app_bundle/__init__.py

   from flask_unchained import AppBundle

   class MyApp(AppBundle):
       commands_module_name = 'cli'
       config_module_name = 'settings'
       views_module_name = 'controllers'

So, while configurable, it's actually hooks that determine the default structure of bundles. You are free to choose whether you want to use single-file modules or multi-file packages; it makes no difference to the default implementation of ``AppFactoryHook``.

Bundles are hierarchical, and can override/extend each other. The way this works, is that by placing something in the same location with the same name as the thing it's meant to override/extend from the parent bundle, the hooks will know to register the correct version, while still inheriting everything else from the parent bundle. Let's take a look at an example.

The security bundle includes templates for its views, located in its ``templates`` folder. If you wanted to override one of those templates, say ``security/login.html``, you would create a template with the same name in your app bundle's ``templates`` folder, ie ``your_app_bundle/templates/security/login.html``. Flask Unchained even allows you to extend the template you're overriding, using the standard Jinja syntax, and it will correctly determine which parent template you're referring to.
