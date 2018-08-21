SQLAlchemy Bundle
-----------------

Integrates `Flask SQLAlchemy <http://flask-sqlalchemy.pocoo.org/2.3/>`_ and `Flask Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_ with Flask Unchained.

Dependencies
^^^^^^^^^^^^

* Flask SQLAlchemy
* Flask Migrate
* SQLAlchemy
* Alembic
* Depending on your database of choice, you might also need a specific driver library.

Installation
^^^^^^^^^^^^

Install dependencies:

.. code:: bash

   $ pip install flask-unchained[sqlalchemy]

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.sqlalchemy',
   ]

Config
^^^^^^

.. automodule:: flask_unchained.bundles.sqlalchemy.config
   :members:

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.sqlalchemy.commands:db
    :prog: flask db
    :show-nested:

API Documentation
^^^^^^^^^^^^^^^^^

:doc:`../api/bundles/sqlalchemy`
