Session Bundle
--------------

Integrates `Flask Session <https://pythonhosted.org/Flask-Session/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* Flask Session
* Dill

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   $ pip install flask-unchained[session]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.session',
   ]

Config
^^^^^^

.. automodule:: flask_unchained.bundles.session.config
   :members:

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/session`
