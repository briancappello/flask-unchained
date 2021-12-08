Admin Bundle
------------

Integrates `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install "flask-unchained[sqlalchemy,session,security,admin]"

Enable the bundle in your ``BUNDLES``:

.. code:: python

   # project-root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.babel',       # required by Security Bundle
       'flask_unchained.bundles.session',     # required by Security Bundle
       'flask_unchained.bundles.sqlalchemy',  # required by Admin Bundle
       'flask_unchained.bundles.security',    # required by Admin Bundle
       'flask_unchained.bundles.admin',
       'app',
   ]

And include the Admin Bundle's routes:

.. code:: python

    # project-root/your_app_bundle/routes.py

    routes = lambda: [
        # ...
        include('flask_unchained.bundles.admin.routes'),
    ]

Config
^^^^^^

.. autoclass:: flask_unchained.bundles.admin.config.Config
   :members:

API Docs
^^^^^^^^

See :doc:`../api/admin-bundle`
