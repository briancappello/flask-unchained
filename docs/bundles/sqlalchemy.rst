SQLAlchemy Bundle
-----------------

Integrates `Flask SQLAlchemy Unchained <https://pypi.org/project/flask-sqlalchemy-unchained/>`_ and `Flask Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_ with Flask Unchained.

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

   pip install "flask-unchained[sqlalchemy]"

And enable the bundle in your ``unchained_config.py``:

.. code:: python

   # your_project_root/unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.sqlalchemy',
       'app',
   ]

Config
^^^^^^

.. automodule:: flask_unchained.bundles.sqlalchemy.config
   :members:
   :noindex:

Usage
^^^^^

Usage of the SQLAlchemy bundle starts with an import:

.. code:: python

   from flask_unchained.bundles.sqlalchemy import db

From there, usage is extremely similar to stock Flask SQLAlchemy, and aside from a few minor gotchyas, you should just be able to copy your models and they should work (please file a bug report if this doesn't work!). The gotchyas you should be aware of are:

- the automatic table naming has slightly different behavior if the model class name has sequential upper-case characters
- any models defined in not-app-bundles must declare themselves as ``class Meta: lazy_mapped = True``
- you must use ``back_populates`` instead of ``backref`` in ``relationship`` declarations (it may be possible to implement support for backrefs, but honestly, using ``back_populates`` is more Pythonic anyway, because Zen of Python)
- many-to-many join tables must be declared as model classes

Furthermore, models in SQLAlchemy Unchained include three columns by default:

.. list-table::
   :header-rows: 1

   * - column name
     - description
   * - ``id``
     - the primary key
   * - ``created_at``
     - a timestamp of when the model got inserted into the database
   * - ``updated_at``
     - a timestamp of the last time the model was updated in the database

These are customizable by declaring meta options. For example to disable timestamping and to rename the primary key column to ``pk``, it would look like this:

.. code:: python

   from flask_unchained.bundles.sqlalchemy import db


   class Foo(db.Model):
       class Meta:
           pk = 'pk'
           created_at = None
           updated_at = None

Models support the following meta options:

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - meta option name
     - default
     - description
   * - table
     - snake_cased model class name
     - The database tablename to use for this model.
   * - pk
     - ``'id'``
     - The name of the primary key column.
   * - created_at
     - ``'created_at'``
     - The name of the row creation timestamp column.
   * - updated_at
     - ``'updated_at'``
     - The name of the most recent row update timestamp column.
   * - repr
     - ``('id',)``
     - Column attributes to include in the automatic ``__repr__``
   * - validation
     - ``True``
     - Whether or not to enable validation on the model for CRUD operations.
   * - mv_for
     - ``None``
     - Used for specifying the name of the model a :attr:`~flask_unchained.bundles.sqlalchemy.SQLAlchemy.MaterializedView` is for, as a string.
   * - relationships
     - ``{}``
     - This is an automatically determined meta option, and is used for determining whether or not a model has the same relationships as its base model. This is useful when you want to override a model from a bundle but change its relationships. The code that determines this is rather experimental, and may not do the right thing. Please report any bugs you come across!

FIXME: Polymorphic Models

Commands
^^^^^^^^

.. click:: flask_unchained.bundles.sqlalchemy.commands:db
    :prog: flask db
    :show-nested:

API Docs
^^^^^^^^

See :doc:`../api/sqlalchemy-bundle`
