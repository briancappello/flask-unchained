Bundles and Bundle Structure
============================

Bundles are the core building blocks of Flask Unchained apps. They are a replacement for both stock Flask extensions and Blueprints. Furthermore they define a configurable folder structure that makes all of your code automatically discovered and registered with the app.

To create a new bundle, create a new package and subclass :class:`~flask_unchained.Bundle` in the package's ``__init__.py``:

.. code:: python

   # your_package_root/__init__.py

   from flask_unchained import Bundle

   class YourBundle(Bundle):
       pass

:class:`~flask_unchained.Bundle` includes some informational class attributes of interest:

.. list-table::
   :header-rows: 1

   * - attribute name
     - description
   * - module_name
     - Top-level module name of the bundle (dot notation). Automatically determined.
   * - name
     - Name of the bundle. Defaults to the snake cased class name.
   * - folder
     - Root directory path of the bundle's package. Automatically determined.
   * - root_folder
     - Root directory path of the bundle. Automatically determined.
   * - template_folder
     - Root directory path of the bundle's template folder. By default, if there exists a folder named ``templates`` in the bundle package, it will be used, otherwise ``None``.
   * - static_folder
     - Root directory path of the bundle's static assets folder. By default, if there exists a folder named ``static`` in the bundle package, it will be used, otherwise ``None``.
   * - static_url_path
     - Url path where this bundle's static assets will be served from. If static_folder is set, this will default to ``/<bundle.name>/static``, otherwise ``None``.

As far as determining the directory structure for the rest of the bundle goes, it is actually subclasses of :class:`~flask_unchained.AppFactoryHook` that set the defaults. (Hooks are what do most of the work of initializing the app.) There are some hooks that always run, and others that will run only if their bundle is configured to load in your ``unchained_config.BUNDLES``. Flask Unchained provides a command to make it easier to discover hooks, what order they run in, and where they load from:

.. code:: bash

   flask unchained hooks
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

In the second column, ``Default Bundle Module``, are the default module names for bundles. The third column, ``Bundle Module Override Attr``, is a list of attribute names that you can set on your :class:`~flask_unchained.Bundle` subclass to customize the respective module the hook will load from. For example:

.. code:: python

   # your_bundle/__init__.py

   from flask_unchained import Bundle

   class YourBundle(Bundle):
       commands_module_name = 'cli'
       config_module_name = 'settings'
       views_module_name = 'controllers'

Extending and Overriding Bundles
--------------------------------

Extending and overriding bundles is pretty simple. All you need to do is subclass the bundle you want to extend in its own python package, and include that package in your ``unchained_config.BUNDLES`` instead of the original bundle. There is no limit to the depth of the bundle hierarchy (other than perhaps your sanity). So, for example, to extend the security bundle, it would look like this:

.. code:: python

   # your_security_bundle/__init__.py

   from flask_unchained.bundles.security import SecurityBundle

   class YourSecurityBundle(SecurityBundle):
       pass

.. code:: python

   # your-project-root/unchained_config.py

   BUNDLES = [
       # ...
       'dotted.module.path.to.your.security.bundle',
       'app',
   ]

Integrating Stock Flask Extensions
----------------------------------

Extensions that can be used with Flask Unchained have a few limitations:

- They must implement ``init_app``, and its signature must take a single argument: ``app``. Some extensions fit this restriction out of the box, but often you need to subclass the extension you want to include to make sure its ``init_app`` function signature matches.
- For consistency with other Flask Unchained bundles, it is strongly recommended to *not* set configuration defaults/values via the extension, but instead in the bundle's ``Config`` classes. Sometimes this means you will need to create a few new options to replace arguments that were originally passed into the extension's ``init_app`` method.
- Extensions must not register any cli commands themselves.
- Extensions must not register any views themselves (and must not use Blueprints) [in practice, this usually means you need to rewrite all the views as Controllers].

In order for Flask Unchained to actually discover and initialize the extension you want to include, it must be placed in your bundle's ``extensions`` module. It looks like this:

.. code:: python

   # your_bundle/extensions.py

   from flask_whatever import WhateverExtension

   whatever = WhateverExtension()

   EXTENSIONS = {
       'whatever': whatever,
   }

The keys of the ``EXTENSIONS`` dictionary serve as the name that will be used to reference the extension at runtime (and for dependency injection, although typically you would just import the instance from your bundle). There can be multiple extensions per bundle, and you can also declare other extensions as dependencies that must be initialized before yours:

.. code:: python

   EXTENSIONS = {
       'whatever': (whatever, ['dep_ext_one', 'dep_ext_two']),
   }

Bundle Config
-------------

Flask Unchained is only designed to work with class-based configs, and it will look for them (by default) in the ``config`` module of your bundle. First the options from the ``Config`` class are loaded, and then if an env-specific config class exists, we then load options from it (possibly overwriting settings from ``Config``). It's worth noting is that all of the config classes are optional; if they don't exist Flask Unchained will simply skip trying to load them.

.. code:: python

   class Config:
       OPTION_ONE = 'value'
       OPTION_TWO = 'value'

   class DevConfig(Config):
       pass

   class ProdConfig(Config):
       pass

   class StagingConfig(Config):
       pass

   class TestConfig(Config):
       pass

Shown above are the five class names that Flask Unchained recognizes for configuration classes. Configuration is otherwise the same as stock Flask, and therefore any non-uppercase attributes will be ignored when the class gets loaded.

Services and Dependency Injection
---------------------------------

Flask Unchained supports dependency injection of services and extensions (by default). Here a "service" means any subclass of :class:`~flask_unchained.BaseService` that lives in a bundle's ``services`` module (or that gets imported there). You can however manually register anything as a "service", even plain values if you really wanted to, using :meth:`flask_unchained.Unchained.register_service`. It's worth noting that services can request other services be injected into them, and as long as there are no circular dependencies, it will work. The names of services must be unique across your app, and by default are named as the snake-cased class name, so if there any conflicting class names then you will need to use :meth:`~flask_unchained.Unchained.service` to customize the name the service gets registered under.

App Bundle Special Behaviors
----------------------------

The app bundle gets loaded last, and can therefore override anything from other bundles. Otherwise everything is the same as for regular bundles.

In order to declare a bundle as the app bundle, you must subclass :class:`~flask_unchained.AppBundle`:

.. code:: python

   # your-project-root/your_app_bundle/__init__.py

   from flask_unchained import AppBundle


   class App(AppBundle):
       pass
