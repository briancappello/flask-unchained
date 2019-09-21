Configuration
-------------

Configuring Flask Unchained
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You configure Flask Unchained by placing a file named ``unchained_config.py`` in your project's root folder. The purpose of ``unchained_config.py`` is to define which bundles to load and the keyword arguments passed to the :class:`~flask_unchained.FlaskUnchained` constructor (which takes the same arguments as the original :class:`~flask.Flask` constructor). It typically will look something like this (only ``ROOT_PATH`` and the ``BUNDLES`` list with your app bundle are required)::

   # your-project-root/unchained_config.py

   import os


   ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


   def folder_or_none(folder_name):
       folder = os.path.join(ROOT_PATH, folder_name)
       return folder if os.path.exists(folder) else None


   # upper-cased variables get passed as kwargs to `AppFactory.FLASK_APP_CLASS.__init__`
   # (by default, `:class:FlaskUnchained`, which has the same constructor as :class:`flask.Flask`)
   TEMPLATE_FOLDER = folder_or_none('templates')
   STATIC_FOLDER = folder_or_none('static')
   STATIC_URL_PATH = '/static' if STATIC_FOLDER else None

   # the list of bundle modules to load (in dot-module-notation)
   BUNDLES = [
       'app',  # your app bundle *must* be last
   ]

App Bundle Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

In order to configure your app, Flask Unchained uses specifically named per-environment classes::

   # your_app_bundle/config.py

   import os

   from flask_unchained import AppBundleConfig


   class Config(AppBundleConfig):
       """Options set here will be configured for all environments."""

       # SECRET_KEY is the only required setting
       SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-to-a-secret-key')

   class DevConfig(Config):
       """Options specific to the development environment."""

   class ProdConfig(Config):
       """Options specific to the production environment."""

   class StagingConfig(ProdConfig):
       """Options specific to the staging environment."""

   class TestConfig(Config):
       """Options specific to the testing environment."""

Configuration settings get loaded (by the :class:`~flask_unchained.hooks.ConfigureAppHook` class) in a specific order. For each of the steps below, "the bundle config" means the merged configuration settings from ``Config`` and the environment-specific configuration class (if one or both exists, with the env-specific settings taking precedence):

1) The defaults settings defined within Flask Unchained itself get loaded. At the time of writing, the only defaults it sets are the ``DEBUG`` option (pulled from the ``FLASK_DEBUG`` environment variable), and only when ``env == 'test'``, ``TESTING = True`` and ``WTF_CSRF_ENABLED = False``.
2) Your app bundle's config gets loaded.
3) The settings from all of the bundles listed in your ``unchained_config.BUNDLES`` get loaded (in the order the bundles were listed). Using ``BundleConfig.current_app.config``, bundles can access the app's current configuration settings at the point in time that bundle is being configured.
4) Your app bundle's config gets loaded once again, to make sure its settings have the final say.

**IMPORTANT: The** ``Config`` **class is required for your app bundle.**

Bundle Configuration
^^^^^^^^^^^^^^^^^^^^

Configuring standard bundles is almost the same, the only differences being:

1) Configuration is entirely optional for standard bundles
2) When a bundle does need to set configuration options, it should subclass :class:`~flask_unchained.BundleConfig`::

   # your_bundle/config.py

   from flask_unchained import BundleConfig

   class Config(BundleConfig):
       pass
