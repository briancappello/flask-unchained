The Unchained Extension
-----------------------

The :class:`~flask_unchained.Unchained` extension will then register itself with the app, and run all of the discovered hooks. Hooks are subclasses of :class:`~flask_unchained.AppFactoryHook`, and they are loaded from both core Flask Unchained as well as from the ``hooks`` module of each bundle listed in ``unchained_config.BUNDLES``. Hooks are responsible for the majority of the hard work required to initialize the application. They do things like loading configuration from all the bundles, initializing extensions, discovering models, and registering views and routes with Flask - to name some examples.
