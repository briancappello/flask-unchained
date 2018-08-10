Admin Bundle
------------

Integrates `Flask Admin <https://flask-admin.readthedocs.io/en/latest/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* flask-admin >= 1.5

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

.. automodule:: flask_unchained.bundles.admin.config
   :members:

API Documentation
^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.bundles.admin
   :members:

Extensions
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.admin.extensions
   :members:

Forms
~~~~~

.. automodule:: flask_unchained.bundles.admin.forms
   :members:

Hooks
~~~~~

.. automodule:: flask_unchained.bundles.admin.hooks
   :members:

Macro
~~~~~

.. automodule:: flask_unchained.bundles.admin.macro
   :members:

Model Admin
~~~~~~~~~~~

.. automodule:: flask_unchained.bundles.admin.model_admin
   :members:

Security
~~~~~~~~

.. automodule:: flask_unchained.bundles.admin.security
   :members:

Views
~~~~~

.. automodule:: flask_unchained.bundles.admin.views
   :members:
