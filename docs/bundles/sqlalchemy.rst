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

.. automodule:: flask_unchained.bundles.sqlalchemy
   :members:

Extensions
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.extensions
   :members:

Hooks
~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.hooks
   :members:

Metaclasses
~~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.meta
   :members:

Services
~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.services
   :members:

sqla
~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.sqla
   :members:

Base Model
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.base_model
   :members:

Base Query
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.base_query
   :members:

Model Form
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.model_form
   :members:

Validation
~~~~~~~~~~

.. automodule:: flask_unchained.bundles.sqlalchemy.validation
   :members: