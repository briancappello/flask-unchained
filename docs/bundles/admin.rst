Admin Bundle
------------

Integrates `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   $ pip install flask-unchained[admin]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.admin',
   ]

Config
^^^^^^

.. autoclass:: flask_unchained.bundles.admin.config.Config
   :members:

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/admin`
