Setting up the Database
-----------------------

Flask Unchained comes integrated with the `SQLAlchemy <http://www.sqlalchemy.org/>`_ ORM. It is currently the only ORM supported by Flask Unchained, however pull requests are always welcome!

Install Dependencies
^^^^^^^^^^^^^^^^^^^^

First we need to install SQLAlchemy and related dependencies:

.. code:: bash

   pip install flask-unchained[sqlalchemy]

We also need to update our tests so that they load the pytest fixtures from the SQLAlchemy Bundle:

.. code:: bash

   touch tests/conftest.py

.. code:: python

   # tests/conftest.py

   from flask_unchained.bundles.sqlalchemy.pytest import *

There are two fixtures that it includes: ``db`` and ``db_session``. They're both automatically used; ``db`` is scoped ``session`` and will create/drop all necessary tables once per test session while ``db_session`` is function scoped, and thus will run for every test. Its responsibility is to create an isolated session of transactions for each individual test, to make sure that every test starts with a clean slate database without needing to drop and recreate all the tables for each and every test.

Next, enable the SQLAlchemy Bundle so we can begin using it:

.. code:: python

   # unchained_config.py

   BUNDLES = [
       # ...
       'flask_unchained.bundles.sqlalchemy',
       'app',
   ]

Configuration
^^^^^^^^^^^^^

By default, the SQLAlchemy Bundle is configured to use an SQLite database. For the sake of simplicity, we'll leave the defaults as-is. The SQLite file will be stored at ``db/<env>.sqlite``.

If you'd like to change this, it would look like this:

.. code:: python

   # app/config.py

   class Config:
      # ...
      SQLALCHEMY_DATABASE_URI = 'sqlite:///db/flaskr.sqlite'

If you're fine using SQLite, continue to :ref:`init-migrations`.

If instead you'd like to use MariaDB/MySQL or PostgreSQL, now would be the time to configure it. For example, to use PostgreSQL with ``psycopg2``:

.. code:: python

   # app/config.py

   class Config(AppConfig):
       # ...
       SQLALCHEMY_DATABASE_URI = '{engine}://{user}:{pw}@{host}:{port}/{db}'.format(
           engine=os.getenv('FLASK_DATABASE_ENGINE', 'postgresql+psycopg2'),
           user=os.getenv('FLASK_DATABASE_USER', 'flaskr'),
           pw=os.getenv('FLASK_DATABASE_PASSWORD', 'flaskr'),
           host=os.getenv('FLASK_DATABASE_HOST', '127.0.0.1'),
           port=os.getenv('FLASK_DATABASE_PORT', 5432),
           db=os.getenv('FLASK_DATABASE_NAME', 'flaskr'))

   class TestConfig:
       # ...
       SQLALCHEMY_DATABASE_URI = '{engine}://{user}:{pw}@{host}:{port}/{db}'.format(
           engine=os.getenv('FLASK_DATABASE_ENGINE', 'postgresql+psycopg2'),
           user=os.getenv('FLASK_DATABASE_USER', 'flaskr_test'),
           pw=os.getenv('FLASK_DATABASE_PASSWORD', 'flaskr_test'),
           host=os.getenv('FLASK_DATABASE_HOST', '127.0.0.1'),
           port=os.getenv('FLASK_DATABASE_PORT', 5432),
           db=os.getenv('FLASK_DATABASE_NAME', 'flaskr_test'))

Or for MariaDB/MySQL, replace the ``engine`` parameter with ``mysql+mysqldb`` and the ``port`` parameter with ``3306``.

Note that you'll probably need to install the relevant driver package, eg:

.. code:: bash

   # for psycopg2
   pip install --no-binary psycopg2

   # for mysql
   pip install mysqlclient

See `the upstream docs on SQLAlchemy dialects <http://docs.sqlalchemy.org/en/latest/dialects/index.html>`_ for details.

.. _init-migrations:

Initialize Migrations
^^^^^^^^^^^^^^^^^^^^^

The last step is to initialize the database migrations folder:

.. code:: bash

   flask db init

We should commit our changes before continuing:

.. code:: bash

   git add .
   git status
   git commit -m 'install sqlalchemy bundle'

Next, in order to demonstrate using migrations, and also as preparation for installing the Security Bundle, next let's continue to setting up :doc:`session` using the Session Bundle.
