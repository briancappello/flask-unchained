API Bundle
----------

Integrates `Marshmallow <https://marshmallow.readthedocs.io/en/2.x-line/>`_, `Flask Marshmallow <https://flask-marshmallow.readthedocs.io/en/latest/>`_, and `APISpec <http://apispec.readthedocs.io/en/stable/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* apispec >= 0.39
* marshmallow >= 2.13.6
* marshmallow-sqlalchemy >= 0.13.1
* flask-marshmallow >= 0.8

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   $ pip install flask-unchained[api]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.api',
   ]

API Documentation
^^^^^^^^^^^^^^^^^

.. automodule:: flask_unchained.bundles.api
   :members:

APISpec
~~~~~~~

.. automodule:: flask_unchained.bundles.api.apispec
   :members:

Decorators
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.api.decorators
   :members:

Extensions
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.api.extensions
   :members:

Hooks
~~~~~

.. automodule:: flask_unchained.bundles.api.hooks
   :members:

Model Resource
~~~~~~~~~~~~~~

.. automodule:: flask_unchained.bundles.api.model_resource
   :members:

Model Serializer
~~~~~~~~~~~~~~~~

.. automodule:: flask_unchained.bundles.api.model_serializer
   :members:

Utils
~~~~~

.. automodule:: flask_unchained.bundles.api.utils
   :members:
