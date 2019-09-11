The App Factory
---------------

Flask Unchained implements the application factory pattern. There is one entry point,
:meth:`flask_unchained.AppFactory().create_app`:

.. code:: python

   # project-root/wsgi.py

   import os

   from flask_unchained import AppFactory, PROD


   app = AppFactory().create_app(os.getenv('FLASK_ENV', PROD))

(In development and testing, this happens automatically behind the scenes when you call
the ``flask`` and ``pytest`` commands.)

The :meth:`~flask_unchained.AppFactory().create_app` classmethod does the following:

1. It load's your project's ``unchained_config`` module.

2. It initializes all of the :class:`~flask_unchained.Bundle` subclasses from those listed in your ``unchained_config.BUNDLES`` list.

3. It initializes a :class:`~flask_unchained.FlaskUnchained` application instance (which is only a minimally extended :class:`~flask.Flask` subclass).

4. For each bundle, it calls :meth:`~flask_unchained.Bundle.before_init_app`.

5. It then initializes the :class:`~flask_unchained.Unchained` extension, by calling ``unchained.init_app(app, env, bundles)``.

6. And once again for each bundle, the app factory calls :meth:`~flask_unchained.Bundle.after_init_app`.

7. Lastly, :meth:`~flask_unchained.AppFactory().create_app` returns the :class:`~flask_unchained.FlaskUnchained` application instance, ready to rock and roll.
