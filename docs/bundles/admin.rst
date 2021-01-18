Admin Bundle
------------

Integrates `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install "flask-unchained[admin]"

Enable the bundle in your ``unchained_config.py``:

.. code:: python

   # project-root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.admin',
       'app',
   ]

And include the Admin Bundle's routes:

.. code:: python

    # project-root/your_app_bundle/routes.py

    routes = lambda: [
        include('flask_unchained.bundles.admin.routes'),
        # ...
    ]

Config
^^^^^^

.. autoclass:: flask_unchained.bundles.admin.config.Config
   :members:

API Docs
^^^^^^^^

See :doc:`../api/admin-bundle`
