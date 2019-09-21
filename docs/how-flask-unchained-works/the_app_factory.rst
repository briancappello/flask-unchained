The App Factory
---------------

How to use it
^^^^^^^^^^^^^

Flask Unchained implements the application factory pattern. There is one entry point,
:meth:`flask_unchained.AppFactory().create_app`:

.. code:: python

   # project-root/wsgi.py

   import os

   from flask_unchained import AppFactory, PROD


   app = AppFactory().create_app(os.getenv('FLASK_ENV', PROD))

(In development and testing, this happens automatically behind the scenes when you call
the ``flask`` and ``pytest`` commands.)

How it works
^^^^^^^^^^^^

The :meth:`~flask_unchained.AppFactory().create_app` method does the following:

1. It load's your project's ``unchained_config`` module and all of the :class:`~flask_unchained.Bundle` subclasses from those listed in your ``unchained_config.BUNDLES`` list.

2. It initializes an application instance using `AppFactory.APP_CLASS` (by default, :class:`~flask_unchained.FlaskUnchained`, which is only a minimally extended subclass of :class:`~flask.Flask`).

3. For each bundle, it calls :meth:`~flask_unchained.Bundle.before_init_app`.

4. It then initializes the :class:`~flask_unchained.Unchained` extension, by calling ``unchained.init_app(app, env, bundles)``. (See :doc:`the_unchained_extension`)

5. And once again for each bundle, the app factory calls :meth:`~flask_unchained.Bundle.after_init_app`.

6. Lastly, :meth:`~flask_unchained.AppFactory().create_app` returns the application instance, ready to rock and roll.

Using a custom subclass of FlaskUnchained
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You just call ``AppFactory.set_app_class`` with your :class:`~flask_unchained.FlaskUnchained` subclass:

.. code:: python

   # project-root/unchained_config.py

   from flask_unchained import AppFactory, FlaskUnchained


   class YourFlaskUnchainedSubclass(FlaskUnchained):
       # your awesome stuffs


   AppFactory.set_app_class(YourFlaskUnchainedSubclass)

   # ... the rest of your config
