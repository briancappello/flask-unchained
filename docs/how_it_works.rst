How it Works
============

The App Factory
---------------

Flask Unchained implements the application factory pattern. There is one entry point:

.. code:: python

   from flask_unchained import AppFactory

   app = AppFactory.create_app(env)

It does the following:

1. Load's your project's ``unchained_config`` module.

2. Initializes all of the ``Bundle`` subclasses from the bundles listed in ``unchained_config.BUNDLES``.

3. Initializes a ``FlaskUnchained`` app instance.

4. For each bundle, call ``bundle.before_init_app(app)``.

5. Calls ``unchained.init_app(app, env, bundles)``.

   The ``Unchained`` extension will then register itself with the app, and it calls ``RunHooksHook.run_hook(app, bundles)``. Hooks are subclasses of ``AppFactoryHook``, and the ``RunHooksHook`` will discover them in both core Flask Unchained as well as in bundles' ``hooks`` module. It is hooks that are responsible for the majority of the hard work required to initialize the application. Hooks do things like loading configuration from all the bundles, initializing extensions, discovering models, and registering views and routes - to name a few examples.

6. For each bundle, call ``bundle.after_init_app(app)``.

Hooks and Bundle Structure
--------------------------

Generally speaking, hooks are responsible for importing and discovering code, and then typically somehow registering those things with the app. They run in a specific order, determined dynamically from each hook's listed dependencies. Each hook can define an attribute, ``bundle_module_name``, that determines the module name in bundles that the hook will load from. Flask Unchained provides a command to make it easier to discover hooks and the location they load from:

.. code:: bash

   $ flask unchained hooks
   ================================================================================
   Hooks
   ================================================================================
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
