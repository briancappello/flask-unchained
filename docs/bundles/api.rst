API Bundle
----------

Integrates `Marshmallow <https://marshmallow.readthedocs.io/en/2.x-line/>`_, `Flask Marshmallow <https://flask-marshmallow.readthedocs.io/en/latest/>`_, and `APISpec <http://apispec.readthedocs.io/en/stable/>`_ with Flask Unchained.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   pip install flask-unchained[api]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.api',
   ]

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/api`
